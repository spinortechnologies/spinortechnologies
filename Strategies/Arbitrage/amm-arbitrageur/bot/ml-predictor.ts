import { BigNumber } from 'ethers';
import { PoolEdge, MultiHopPath } from './tokens';

export interface MarketFeatures {
  priceSpread: number;
  priceVolatility: number;
  avgPrice: number;
  minLiquidity: number;
  avgLiquidity: number;
  liquidityImbalance: number;
  totalVolume24h: number;
  volumeImbalance: number;
  pathLength: number;
  uniqueDexes: number;
  avgFee: number;
  gasPrice: number;
  blockNumber: number;
  timestamp: number;
}

export interface TrainingExample {
  features: MarketFeatures;
  target: number;
  executed: boolean;
}

export class MLPredictor {
  private model: {
    weights: Map<string, number>;
    bias: number;
    learningRate: number;
  };
  private trainingData: TrainingExample[] = [];
  private isTrained = false;
  
  constructor() {
    this.model = {
      weights: new Map<string, number>(),
      bias: 0,
      learningRate: 0.01
    };
  }
  
  public extractFeatures(
    path: MultiHopPath,
    pools: PoolEdge[],
    tokenPrices: Map<string, number>,
    gasPrice: BigNumber,
    blockNumber: number
  ): MarketFeatures {
    const prices: number[] = [];
    const liquidities: number[] = [];
    const fees: number[] = [];
    const dexes = new Set<string>();
    
    for (const edge of path.edges) {
      const price = tokenPrices.get(edge.tokenIn) || 0;
      const liquidity = Number(edge.reserveIn) * price;
      
      prices.push(price);
      liquidities.push(liquidity);
      fees.push(edge.feeBps);
      dexes.add(edge.dex);
    }
    
    const priceSpread = Math.max(...prices) - Math.min(...prices);
    const priceVolatility = this.calculateVolatility(prices);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
    
    const minLiquidity = Math.min(...liquidities);
    const avgLiquidity = liquidities.reduce((a, b) => a + b, 0) / liquidities.length;
    const liquidityImbalance = this.calculateVariance(liquidities);
    
    const totalVolume24h = avgLiquidity * 0.1; // Mock volume
    const volumeImbalance = this.calculateVariance(liquidities);
    
    const avgFee = fees.reduce((a, b) => a + b, 0) / fees.length;
    
    return {
      priceSpread,
      priceVolatility,
      avgPrice,
      minLiquidity,
      avgLiquidity,
      liquidityImbalance,
      totalVolume24h,
      volumeImbalance,
      pathLength: path.edges.length,
      uniqueDexes: dexes.size,
      avgFee,
      gasPrice: Number(gasPrice.toString()) / 1e9, // Convert to gwei
      blockNumber,
      timestamp: Date.now()
    };
  }
  
  public predictConfidence(features: MarketFeatures): number {
    if (!this.isTrained) {
      return 0.5;
    }
    
    let prediction = this.model.bias;
    
    for (const [key, value] of Object.entries(features)) {
      const weight = this.model.weights.get(key) || 0;
      prediction += weight * value;
    }
    
    return 1 / (1 + Math.exp(-prediction));
  }
  
  public train(examples: TrainingExample[]) {
    this.trainingData.push(...examples);
    
    const epochs = 100;
    const batchSize = Math.min(32, this.trainingData.length);
    
    for (let epoch = 0; epoch < epochs; epoch++) {
      const batch = this.getRandomBatch(batchSize);
      
      for (const example of batch) {
        const prediction = this.predictConfidence(example.features);
        const error = example.target - prediction;
        
        for (const [key, value] of Object.entries(example.features)) {
          const currentWeight = this.model.weights.get(key) || 0;
          const newWeight = currentWeight + this.model.learningRate * error * value;
          this.model.weights.set(key, newWeight);
        }
        
        this.model.bias += this.model.learningRate * error;
      }
    }
    
    this.isTrained = true;
  }
  
  private calculateVolatility(values: number[]): number {
    if (values.length < 2) return 0;
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    return Math.sqrt(variance);
  }
  
  private calculateVariance(values: number[]): number {
    if (values.length < 2) return 0;
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    return values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  }
  
  private getRandomBatch(size: number): TrainingExample[] {
    const shuffled = [...this.trainingData].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, size);
  }
} 