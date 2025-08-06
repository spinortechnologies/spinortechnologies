#!/usr/bin/env python3
"""
Enhanced Real-time Paper Integration System
Author: SPINOR Technologies
Date: August 6, 2025
Version: 4.0 - Enhanced Integration

Advanced system for fetching, processing, and integrating recent financial papers
into the AI knowledge base with improved learning capabilities.
"""

import os
import sys
import json
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

# ArXiv integration
try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    logging.info("ArXiv not available - using sample papers")

# Vector database integration
try:
    from vector_db import VectorStore
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedPaperIntegrator:
    """Enhanced system for fetching and integrating financial papers."""
    
    def __init__(self):
        """Initialize the enhanced paper integrator."""
        self.categories = [
            "q-fin.PR",  # Pricing of Securities
            "q-fin.RM",  # Risk Management  
            "q-fin.PM",  # Portfolio Management
            "q-fin.TR",  # Trading and Market Microstructure
            "q-fin.MF",  # Mathematical Finance
            "q-fin.CP",  # Computational Finance
            "q-fin.GN",  # General Finance
            "math.PR",   # Probability (relevant for finance)
            "stat.AP",   # Applied Statistics
        ]
        
        # Enhanced keyword sets for better paper filtering
        self.english_keywords = [
            "quantitative finance", "option pricing", "risk management",
            "portfolio optimization", "algorithmic trading", "derivatives",
            "black-scholes", "value at risk", "monte carlo", "stochastic",
            "volatility", "hedge", "arbitrage", "capm", "markowitz",
            "financial modeling", "market risk", "credit risk", "liquidity",
            "high frequency trading", "machine learning finance"
        ]
        
        self.spanish_keywords = [
            "finanzas cuantitativas", "valuación opciones", "gestión riesgo",
            "optimización portafolio", "trading algorítmico", "derivados",
            "valor en riesgo", "monte carlo", "estocástico", "volatilidad",
            "cobertura", "arbitraje", "modelado financiero", "riesgo mercado"
        ]
        
        # Create directories
        self.data_dir = Path("./data/papers")
        self.processed_dir = Path("./data/processed_papers")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge extraction patterns
        self.concept_patterns = {
            'black_scholes': [
                r'black.scholes', r'option.pricing', r'european.option',
                r'geometric.brownian', r'risk.neutral'
            ],
            'var': [
                r'value.at.risk', r'var\b', r'risk.measure', r'quantile',
                r'expected.shortfall', r'conditional.var'
            ],
            'portfolio': [
                r'portfolio.optimization', r'markowitz', r'efficient.frontier',
                r'mean.variance', r'asset.allocation', r'diversification'
            ],
            'monte_carlo': [
                r'monte.carlo', r'simulation', r'random.sampling',
                r'path.dependent', r'numerical.method'
            ],
            'derivatives': [
                r'derivative', r'option', r'future', r'forward', r'swap',
                r'exotic.option', r'american.option'
            ]
        }
        
        logger.info("🚀 Enhanced Paper Integrator initialized")
    
    async def fetch_and_process_papers(self, days_back: int = 3, max_papers: int = 50) -> Dict[str, Any]:
        """
        Fetch and process recent papers with enhanced filtering.
        
        Args:
            days_back: Number of days to look back
            max_papers: Maximum number of papers to fetch
            
        Returns:
            Dictionary with processing results
        """
        if not ARXIV_AVAILABLE:
            logger.warning("ArXiv not available - creating sample papers")
            return self._create_sample_papers()
        
        try:
            logger.info(f"🔍 Fetching papers from last {days_back} days...")
            
            all_papers = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Fetch from multiple categories
            for category in self.categories[:6]:  # Limit to main finance categories
                try:
                    logger.info(f"📚 Searching category: {category}")
                    
                    # Build search query
                    search = arxiv.Search(
                        query=f"cat:{category}",
                        max_results=max_papers // len(self.categories),
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                        sort_order=arxiv.SortOrder.Descending
                    )
                    
                    papers_found = 0
                    for paper in search.results():
                        if paper.published.replace(tzinfo=None) < cutoff_date:
                            break
                        
                        # Enhanced relevance filtering
                        if self._is_relevant_paper(paper):
                            processed_paper = self._process_paper(paper)
                            all_papers.append(processed_paper)
                            papers_found += 1
                        
                        if papers_found >= 10:  # Limit per category
                            break
                    
                    logger.info(f"✅ Found {papers_found} relevant papers in {category}")
                    
                except Exception as e:
                    logger.error(f"Error fetching from {category}: {e}")
                    continue
            
            # Sort by relevance score and published date
            all_papers.sort(key=lambda x: (x['relevance_score'], x['published']), reverse=True)
            all_papers = all_papers[:max_papers]
            
            # Save processed papers
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"papers_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_papers, f, indent=2, ensure_ascii=False, default=str)
            
            # Extract and save knowledge concepts
            knowledge_concepts = self._extract_knowledge_concepts(all_papers)
            concepts_file = self.processed_dir / f"concepts_{timestamp}.json"
            
            with open(concepts_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_concepts, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Successfully processed {len(all_papers)} papers")
            logger.info(f"📁 Saved to: {output_file}")
            logger.info(f"🧠 Extracted {len(knowledge_concepts)} knowledge concepts")
            
            return {
                'success': True,
                'papers_processed': len(all_papers),
                'file_path': str(output_file),
                'concepts_extracted': len(knowledge_concepts),
                'concepts_file': str(concepts_file),
                'categories_searched': len(self.categories),
                'processing_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in paper processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'papers_processed': 0
            }
    
    def _is_relevant_paper(self, paper) -> bool:
        """Enhanced relevance checking for papers."""
        title = paper.title.lower()
        summary = paper.summary.lower()
        combined_text = f"{title} {summary}"
        
        # Check for financial keywords
        keyword_score = 0
        
        # English keywords
        for keyword in self.english_keywords:
            if keyword.lower() in combined_text:
                keyword_score += 1
        
        # Spanish keywords
        for keyword in self.spanish_keywords:
            if keyword.lower() in combined_text:
                keyword_score += 1
        
        # Check for mathematical finance terms
        math_terms = [
            'stochastic', 'brownian', 'diffusion', 'volatility', 'correlation',
            'optimization', 'numerical', 'algorithm', 'model', 'pricing'
        ]
        
        for term in math_terms:
            if term in combined_text:
                keyword_score += 0.5
        
        # Minimum threshold for relevance
        return keyword_score >= 2
    
    def _process_paper(self, paper) -> Dict[str, Any]:
        """Process and enhance paper information."""
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(paper)
        
        # Extract key concepts
        concepts = self._extract_paper_concepts(paper)
        
        # Determine languages
        languages = self._detect_paper_languages(paper)
        
        return {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'published': paper.published,
            'updated': paper.updated,
            'summary': paper.summary,
            'arxiv_id': paper.entry_id.split('/')[-1],
            'pdf_url': paper.pdf_url,
            'categories': paper.categories,
            'relevance_score': relevance_score,
            'extracted_concepts': concepts,
            'languages': languages,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_relevance_score(self, paper) -> float:
        """Calculate relevance score for paper ranking."""
        title = paper.title.lower()
        summary = paper.summary.lower()
        combined_text = f"{title} {summary}"
        
        score = 0.0
        
        # High-value keywords (higher weight)
        high_value_keywords = [
            'black-scholes', 'value at risk', 'portfolio optimization',
            'monte carlo', 'option pricing', 'risk management'
        ]
        
        for keyword in high_value_keywords:
            if keyword in combined_text:
                score += 3.0
        
        # Medium-value keywords
        medium_value_keywords = [
            'derivative', 'volatility', 'stochastic', 'optimization',
            'financial', 'quantitative', 'trading', 'market'
        ]
        
        for keyword in medium_value_keywords:
            if keyword in combined_text:
                score += 1.0
        
        # Recency bonus (more recent papers get higher scores)
        days_old = (datetime.now() - paper.published.replace(tzinfo=None)).days
        if days_old <= 1:
            score += 2.0
        elif days_old <= 7:
            score += 1.0
        
        return round(score, 2)
    
    def _extract_paper_concepts(self, paper) -> List[str]:
        """Extract financial concepts from paper."""
        title = paper.title.lower()
        summary = paper.summary.lower()
        combined_text = f"{title} {summary}"
        
        found_concepts = []
        
        for concept, patterns in self.concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    found_concepts.append(concept)
                    break
        
        return list(set(found_concepts))
    
    def _detect_paper_languages(self, paper) -> List[str]:
        """Detect languages present in paper."""
        # Simple heuristic based on common words
        title = paper.title.lower()
        summary = paper.summary.lower()
        
        languages = ['en']  # Default to English
        
        # Check for Spanish indicators
        spanish_indicators = [
            'finanzas', 'riesgo', 'modelo', 'análisis', 'mercado',
            'precio', 'valor', 'gestión', 'optimización'
        ]
        
        if any(indicator in f"{title} {summary}" for indicator in spanish_indicators):
            languages.append('es')
        
        return languages
    
    def _extract_knowledge_concepts(self, papers: List[Dict]) -> Dict[str, Any]:
        """Extract structured knowledge concepts from all papers."""
        knowledge = {
            'concepts': {},
            'authors': {},
            'trending_topics': [],
            'methodologies': {},
            'applications': {}
        }
        
        # Process each paper
        for paper in papers:
            # Concept extraction
            for concept in paper.get('extracted_concepts', []):
                if concept not in knowledge['concepts']:
                    knowledge['concepts'][concept] = {
                        'papers': [],
                        'frequency': 0,
                        'recent_developments': []
                    }
                
                knowledge['concepts'][concept]['papers'].append({
                    'title': paper['title'][:100],
                    'authors': paper['authors'][:3],
                    'arxiv_id': paper['arxiv_id'],
                    'relevance_score': paper['relevance_score']
                })
                knowledge['concepts'][concept]['frequency'] += 1
            
            # Author tracking
            for author in paper['authors'][:3]:  # Limit to first 3 authors
                if author not in knowledge['authors']:
                    knowledge['authors'][author] = {
                        'papers': [],
                        'concepts': set()
                    }
                
                knowledge['authors'][author]['papers'].append(paper['title'][:50])
                knowledge['authors'][author]['concepts'].update(paper.get('extracted_concepts', []))
        
        # Convert sets to lists for JSON serialization
        for author_data in knowledge['authors'].values():
            author_data['concepts'] = list(author_data['concepts'])
        
        # Find trending topics (most frequent concepts)
        concept_frequencies = [(concept, data['frequency']) 
                             for concept, data in knowledge['concepts'].items()]
        concept_frequencies.sort(key=lambda x: x[1], reverse=True)
        knowledge['trending_topics'] = [concept for concept, freq in concept_frequencies[:10]]
        
        return knowledge
    
    def _create_sample_papers(self) -> Dict[str, Any]:
        """Create sample papers when ArXiv is not available."""
        sample_papers = [
            {
                'title': 'Enhanced Black-Scholes Model with Stochastic Volatility',
                'authors': ['Jane Smith', 'John Doe'],
                'published': datetime.now().isoformat(),
                'summary': 'This paper presents an enhanced version of the Black-Scholes model incorporating stochastic volatility for more accurate option pricing.',
                'arxiv_id': 'sample001',
                'relevance_score': 8.5,
                'extracted_concepts': ['black_scholes', 'volatility'],
                'languages': ['en']
            },
            {
                'title': 'Optimización de Portafolios con Métodos Monte Carlo',
                'authors': ['María García', 'Carlos López'],
                'published': datetime.now().isoformat(),
                'summary': 'Análisis de técnicas de optimización de portafolios utilizando simulaciones Monte Carlo para gestión de riesgos.',
                'arxiv_id': 'sample002',
                'relevance_score': 7.8,
                'extracted_concepts': ['portfolio', 'monte_carlo'],
                'languages': ['es', 'en']
            },
            {
                'title': 'Value at Risk Models for Cryptocurrency Markets',
                'authors': ['Alice Johnson', 'Bob Wilson'],
                'published': datetime.now().isoformat(),
                'summary': 'Comprehensive analysis of VaR models applied to cryptocurrency markets with enhanced risk measures.',
                'arxiv_id': 'sample003',
                'relevance_score': 8.2,
                'extracted_concepts': ['var', 'risk_management'],
                'languages': ['en']
            }
        ]
        
        # Save sample papers
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"papers_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_papers, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("✅ Created sample papers for demonstration")
        
        return {
            'success': True,
            'papers_processed': len(sample_papers),
            'file_path': str(output_file),
            'concepts_extracted': 6,
            'is_sample': True
        }
    
    def get_latest_papers_summary(self) -> Dict[str, Any]:
        """Get summary of latest processed papers."""
        try:
            paper_files = list(self.data_dir.glob("papers_*.json"))
            if not paper_files:
                return {'papers': [], 'summary': 'No papers available'}
            
            latest_file = max(paper_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            # Create summary
            summary = {
                'total_papers': len(papers),
                'last_update': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                'top_concepts': [],
                'languages': [],
                'recent_papers': papers[:5]  # First 5 papers
            }
            
            # Extract concepts and languages
            all_concepts = []
            all_languages = []
            
            for paper in papers:
                all_concepts.extend(paper.get('extracted_concepts', []))
                all_languages.extend(paper.get('languages', ['en']))
            
            # Count frequencies
            from collections import Counter
            concept_counts = Counter(all_concepts)
            language_counts = Counter(all_languages)
            
            summary['top_concepts'] = list(concept_counts.keys())[:10]
            summary['languages'] = list(language_counts.keys())
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting papers summary: {e}")
            return {'papers': [], 'summary': f'Error: {e}'}


async def main():
    """Main function for testing the enhanced paper integrator."""
    integrator = EnhancedPaperIntegrator()
    
    print("🚀 SPINOR Enhanced Paper Integration System")
    print("=" * 50)
    
    # Fetch and process papers
    result = await integrator.fetch_and_process_papers(days_back=3, max_papers=20)
    
    print(f"✅ Processing complete:")
    print(f"   📄 Papers processed: {result['papers_processed']}")
    print(f"   🧠 Concepts extracted: {result.get('concepts_extracted', 0)}")
    print(f"   📁 Output file: {result.get('file_path', 'N/A')}")
    
    # Get summary
    summary = integrator.get_latest_papers_summary()
    print(f"\n📊 Summary:")
    print(f"   🔍 Top concepts: {', '.join(summary['top_concepts'][:5])}")
    print(f"   🗣️ Languages: {', '.join(summary['languages'])}")
    

if __name__ == "__main__":
    asyncio.run(main())
