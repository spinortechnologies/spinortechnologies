import { ethers } from 'hardhat';
import { BigNumber } from 'ethers';
import pool from '@ricokahler/pool';
import AsyncLock from 'async-lock';

import { FlashBot } from '../typechain/FlashBot';
import { Network, tryLoadPairs, getTokens, buildPoolGraph, PoolEdge, MultiHopPath, CycleOpportunity } from './tokens';
import { getBnbPrice } from './basetoken-price';
import log from './log';
import config from './config';
import { MLPredictor, MarketFeatures } from './ml-predictor';

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function calcNetProfit(profitWei: BigNumber, address: string, baseTokens: Tokens): Promise<number> {
  let price = 1;
  if (baseTokens.wbnb.address == address) {
    price = await getBnbPrice();
  }
  let profit = parseFloat(ethers.utils.formatEther(profitWei));
  profit = profit * price;

  const gasCost = price * parseFloat(ethers.utils.formatEther(config.gasPrice)) * (config.gasLimit as number);
  return profit - gasCost;
}

// Add new multi-hop functions
function findCycles(
  adj: Map<string, PoolEdge[]>,
  start: string,
  maxHops = 3
): MultiHopPath[] {
  const result: MultiHopPath[] = [];
  const visitedPools = new Set<string>();

  function dfs(curr: string, hops: number, edges: PoolEdge[]) {
    if (hops > maxHops) return;
    
    for (const e of adj.get(curr) || []) {
      if (visitedPools.has(e.pool)) continue;
      
      const next = e.tokenOut;
      visitedPools.add(e.pool);
      edges.push(e);

      if (next === start && edges.length >= 2) {
        result.push({ edges: edges.slice(), startToken: start });
      }
      
      if (edges.length < maxHops) {
        dfs(next, hops + 1, edges);
      }

      edges.pop();
      visitedPools.delete(e.pool);
    }
  }
  
  dfs(start, 0, []);
  return result;
}

function amountOutV2(
  amountIn: BigNumber,
  reserveIn: BigNumber,
  reserveOut: BigNumber,
  feeBps: number
): BigNumber {
  const FEE_DEN = BigNumber.from(1000);
  const feeNumer = FEE_DEN.sub(feeBps);
  const amountInWithFee = amountIn.mul(feeNumer);
  const numerator = amountInWithFee.mul(reserveOut);
  const denominator = reserveIn.mul(FEE_DEN).add(amountInWithFee);
  return numerator.div(denominator);
}

function simulatePathOut(path: MultiHopPath, x0: BigNumber): BigNumber | null {
  let x = x0;
  for (const e of path.edges) {
    if (e.reserveIn.lte(0) || e.reserveOut.lte(0)) return null;
    x = amountOutV2(x, e.reserveIn, e.reserveOut, e.feeBps);
    if (x.lte(0)) return null;
  }
  return x;
}

function optimizeInputTernary(
  path: MultiHopPath,
  xMin: BigNumber,
  xMax: BigNumber,
  steps = 30
): { xStar: BigNumber; outStar: BigNumber } | null {
  let lo = xMin;
  let hi = xMax;
  
  const toFloat = (bn: BigNumber) => Number(ethers.utils.formatEther(bn));
  
  for (let i = 0; i < steps; i++) {
    const m1 = lo.add(hi.sub(lo).div(3));
    const m2 = hi.sub(hi.sub(lo).div(3));
    
    const y1 = simulatePathOut(path, m1);
    const y2 = simulatePathOut(path, m2);
    
    if (!y1 || !y2) return null;

    const p1 = toFloat(y1.sub(m1));
    const p2 = toFloat(y2.sub(m2));

    if (p1 < p2) {
      lo = m1;
    } else {
      hi = m2;
    }
  }
  
  const xStar = lo.add(hi).div(2);
  const outStar = simulatePathOut(path, xStar);
  
  if (!outStar) return null;
  
  return { xStar, outStar };
}

function arbitrageFunc(flashBot: FlashBot, baseTokens: Tokens) {
  const lock = new AsyncLock({ timeout: 2000, maxPending: 20 });
  return async function arbitrage(pair: ArbitragePair) {
    const [pair0, pair1] = pair.pairs;

    let res: [BigNumber, string] & {
      profit: BigNumber;
      baseToken: string;
    };
    try {
      res = await flashBot.getProfit(pair0, pair1);
      log.debug(`Profit on ${pair.symbols}: ${ethers.utils.formatEther(res.profit)}`);
    } catch (err) {
      log.debug(err);
      return;
    }

    if (res.profit.gt(BigNumber.from('0'))) {
      const netProfit = await calcNetProfit(res.profit, res.baseToken, baseTokens);
      if (netProfit < config.minimumProfit) {
        return;
      }

      log.info(`Calling flash arbitrage, net profit: ${netProfit}`);
      try {
        // lock to prevent tx nonce overlap
        await lock.acquire('flash-bot', async () => {
          const response = await flashBot.flashArbitrage(pair0, pair1, {
            gasPrice: config.gasPrice,
            gasLimit: config.gasLimit,
          });
          const receipt = await response.wait(1);
          log.info(`Tx: ${receipt.transactionHash}`);
        });
      } catch (err) {
        if (err.message === 'Too much pending tasks' || err.message === 'async-lock timed out') {
          return;
        }
        log.error(err);
      }
    }
  };
}

// Add new multi-hop arbitrage function
function multiHopArbitrageFunc(flashBot: FlashBot, baseTokens: Tokens, mlPredictor: MLPredictor) {
  const lock = new AsyncLock({ timeout: 2000, maxPending: 20 });
  
  return async function multiHopArbitrage(pairs: ArbitragePair[]) {
    try {
      // Build graph from pairs
      const graph = buildPoolGraph(pairs);
      
      // Find cycles for each base token
      const [baseTokensList] = getTokens(Network.BSC);
      const baseTokenAddresses = Object.values(baseTokensList).map(t => t.address);
      
      for (const baseToken of baseTokenAddresses) {
        const cycles = findCycles(graph, baseToken, config.multiHop.maxHops);
        
        for (const cycle of cycles) {
          // Evaluate cycle with ML
          const tokenPrices = new Map<string, number>();
          tokenPrices.set(baseToken, await getBnbPrice());
          
          const features = mlPredictor.extractFeatures(
            cycle,
            cycle.edges,
            tokenPrices,
            config.gasPrice,
            await ethers.provider.getBlockNumber()
          );
          
          const confidence = mlPredictor.predictConfidence(features);
          
          if (confidence >= config.multiHop.minConfidence) {
            // Optimize input amount
            const xMin = ethers.utils.parseUnits('0.01', 18);
            const xMax = ethers.utils.parseUnits('1', 18); // Simplified
            
            const opt = optimizeInputTernary(cycle, xMin, xMax);
            if (opt) {
              const profit = opt.outStar.sub(opt.xStar);
              const netProfit = await calcNetProfit(profit, baseToken, baseTokens);
              
              if (netProfit >= config.minimumProfit) {
                log.info(`Multi-hop opportunity found: ${netProfit} USD, confidence: ${confidence}`);
                
                // Execute the arbitrage (would need contract support)
                // await executeMultiHopArbitrage(flashBot, cycle, opt.xStar);
              }
            }
          }
        }
      }
    } catch (err) {
      log.debug(err);
    }
  };
}

async function main() {
  const pairs = await tryLoadPairs(Network.BSC);
  const flashBot = (await ethers.getContractAt('FlashBot', config.contractAddr)) as FlashBot;
  const [baseTokens] = getTokens(Network.BSC);
  
  // Initialize ML predictor
  const mlPredictor = new MLPredictor();

  log.info('Start arbitraging');
  while (true) {
    // Original single-hop arbitrage
    await pool({
      collection: pairs,
      task: arbitrageFunc(flashBot, baseTokens),
    });
    
    // Multi-hop arbitrage if enabled
    if (config.multiHop.enabled) {
      await multiHopArbitrageFunc(flashBot, baseTokens, mlPredictor)(pairs);
    }
    
    await sleep(1000);
  }
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    log.error(err);
    process.exit(1);
  });
