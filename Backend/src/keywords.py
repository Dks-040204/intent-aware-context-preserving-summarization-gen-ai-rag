"""
Lightweight keyword extraction
"""

import logging
from typing import List, Dict
import re
from collections import Counter

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extract important keywords from documents (lightweight, no heavy NLP)."""
    
    def __init__(self):
        """Initialize keyword extractor."""
        # Common stopwords
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'more',
            'most', 'other', 'some', 'any', 'such', 'no', 'nor', 'not', 'only',
            'same', 'so', 'than', 'too', 'very', 'just', 'about', 'also', 'our'
        }
    
    def extract_keywords(
        self,
        text: str,
        top_k: int = 10,
        min_length: int = 3
    ) -> List[str]:
        """
        Extract top keywords from text (simple TF approach).
        
        Args:
            text: Input text
            top_k: Number of keywords to extract
            min_length: Minimum keyword length
            
        Returns:
            List of top keywords
        """
        # Clean and lowercase
        text = text.lower()
        
        # Remove special characters and extra spaces
        words = re.findall(r'\b[a-z_]+\b', text)
        
        # Filter stopwords and short words
        filtered_words = [
            w for w in words 
            if w not in self.stopwords and len(w) >= min_length
        ]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        keywords = [word for word, _ in word_freq.most_common(top_k)]
        
        return keywords
    
    def extract_phrases(
        self,
        text: str,
        top_k: int = 5,
        phrase_len: int = 2
    ) -> List[str]:
        """
        Extract key phrases (multi-word terms).
        
        Args:
            text: Input text
            top_k: Number of phrases to extract
            phrase_len: Length of phrases (2-3 words)
            
        Returns:
            List of top phrases
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        phrases = []
        for sentence in sentences:
            words = re.findall(r'\b[a-z_]+\b', sentence.lower())
            # Extract n-grams
            for i in range(len(words) - phrase_len + 1):
                phrase = ' '.join(words[i:i+phrase_len])
                # Skip if contains stopwords
                if not any(w in self.stopwords for w in words[i:i+phrase_len]):
                    phrases.append(phrase)
        
        # Count frequencies
        phrase_freq = Counter(phrases)
        
        # Get top phrases
        top_phrases = [phrase for phrase, _ in phrase_freq.most_common(top_k)]
        
        return top_phrases
    
    def extract_all(
        self,
        text: str,
        keywords_k: int = 10,
        phrases_k: int = 5
    ) -> Dict[str, List[str]]:
        """
        Extract both keywords and phrases.
        
        Args:
            text: Input text
            keywords_k: Number of keywords
            phrases_k: Number of phrases
            
        Returns:
            Dictionary with keywords and phrases
        """
        return {
            'keywords': self.extract_keywords(text, top_k=keywords_k),
            'key_phrases': self.extract_phrases(text, top_k=phrases_k)
        }
    
    def score_keywords(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """
        Score keywords based on frequency and position.
        
        Args:
            text: Input text
            keywords: List of keywords to score
            
        Returns:
            Dictionary with keyword scores
        """
        text_lower = text.lower()
        scores = {}
        
        for keyword in keywords:
            # Count frequency
            count = text_lower.count(keyword)
            
            # Check position (higher score if in beginning)
            position_score = 1.0
            if text_lower.find(keyword) < len(text) / 4:
                position_score = 1.5
            
            # Calculate TF-IDF-like score
            score = (count * position_score) / (len(text.split()) / 100)
            scores[keyword] = min(score, 10.0)  # Cap at 10
        
        return scores
