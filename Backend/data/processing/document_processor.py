"""
Data processing utilities for loading and preparing documents
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and prepare documents for summarization."""
    
    def __init__(self):
        """Initialize document processor."""
        self.documents = []
    
    def load_documents(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load documents from JSON or JSONL file.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of document dictionaries
        """
        documents = []
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        documents = data
                    elif isinstance(data, dict) and 'documents' in data:
                        documents = data['documents']
            
            elif file_path.endswith('.jsonl'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            documents.append(json.loads(line))
            
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            self.documents = documents
            return documents
        
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def save_documents(self, documents: List[Dict], output_path: str) -> bool:
        """
        Save documents to JSON file.
        
        Args:
            documents: List of documents
            output_path: Path to save documents
            
        Returns:
            Success status
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(documents)} documents to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving documents: {str(e)}")
            return False
    
    def process_batch(self, documents: List[Dict]) -> List[Dict]:
        """
        Process a batch of documents.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed documents
        """
        processed = []
        
        for doc in documents:
            processed_doc = {
                'id': doc.get('id', ''),
                'title': doc.get('title', ''),
                'abstract': doc.get('abstract', ''),
                'full_text': doc.get('full_text', ''),
                'sections': doc.get('sections', {}),
                'word_count': len(doc.get('full_text', '').split()),
                'sentence_count': len(doc.get('full_text', '').split('.')),
            }
            processed.append(processed_doc)
        
        return processed
    
    def get_statistics(self, documents: List[Dict] = None) -> Dict[str, Any]:
        """
        Get statistics about documents.
        
        Args:
            documents: Documents to analyze (uses self.documents if None)
            
        Returns:
            Dictionary of statistics
        """
        docs = documents or self.documents
        
        if not docs:
            return {}
        
        word_counts = [len(doc.get('full_text', '').split()) for doc in docs]
        
        return {
            'total_documents': len(docs),
            'total_words': sum(word_counts),
            'average_length': sum(word_counts) / len(docs) if docs else 0,
            'min_length': min(word_counts) if word_counts else 0,
            'max_length': max(word_counts) if word_counts else 0,
        }


class ArxivLoader:
    """Load arXiv dataset."""
    
    @staticmethod
    def load_from_csv(csv_path: str) -> List[Dict]:
        """Load arXiv data from CSV file."""
        import pandas as pd
        
        df = pd.read_csv(csv_path)
        documents = []
        
        for _, row in df.iterrows():
            doc = {
                'id': row.get('id', ''),
                'title': row.get('title', ''),
                'authors': row.get('authors', '').split(';') if 'authors' in row else [],
                'abstract': row.get('abstract', ''),
                'categories': row.get('categories', '').split() if 'categories' in row else [],
                'published_date': row.get('update_date', ''),
            }
            documents.append(doc)
        
        return documents


class PubmedLoader:
    """Load PubMed dataset."""
    
    @staticmethod
    def fetch_from_api(query: str, max_results: int = 10) -> List[Dict]:
        """Fetch PubMed papers via API."""
        import requests
        
        base_url = "https://pubmed.ncbi.nlm.nih.gov/api/gateway/search"
        
        params = {
            'term': query,
            'pageSize': max_results,
            'format': 'json'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            documents = []
            for paper in data.get('papers', []):
                doc = {
                    'id': paper.get('pmid', ''),
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', ''),
                    'authors': paper.get('authors', []),
                    'published_date': paper.get('pubdate', ''),
                }
                documents.append(doc)
            
            return documents
        
        except Exception as e:
            logger.error(f"Error fetching from PubMed: {str(e)}")
            return []


def load_sample_data() -> List[Dict]:
    """Load sample documents for testing."""
    current_dir = Path(__file__).parent.parent
    sample_file = current_dir / 'sample_documents.json'
    
    if sample_file.exists():
        processor = DocumentProcessor()
        return processor.load_documents(str(sample_file))
    
    return []
