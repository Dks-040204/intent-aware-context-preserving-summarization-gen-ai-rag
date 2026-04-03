"""
Intelligent model selection based on document characteristics
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ModelCategory(Enum):
    """Model categories by speed/complexity tradeoff."""
    LIGHTWEIGHT = "lightweight"
    BALANCED = "balanced"
    ADVANCED = "advanced"


class DocumentComplexity(Enum):
    """Document complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ModelSelector:
    """Intelligent model selector based on document characteristics."""
    
    LIGHTWEIGHT_MODELS = {
        't5-small': {'params': 60e6, 'speed': 'very_fast', 'quality': 'good'},
        'distilbart-cnn-6-6': {'params': 82e6, 'speed': 'very_fast', 'quality': 'good'},
        'bart-base': {'params': 140e6, 'speed': 'fast', 'quality': 'very_good'},
    }
    
    BALANCED_MODELS = {
        't5-base': {'params': 220e6, 'speed': 'fast', 'quality': 'excellent'},
        'pegasus-arxiv': {'params': 568e6, 'speed': 'moderate', 'quality': 'excellent'},
        'bart-large-cnn': {'params': 406e6, 'speed': 'moderate', 'quality': 'excellent'},
    }
    
    ADVANCED_MODELS = {
        'llama-7b': {'params': 7e9, 'speed': 'slow', 'quality': 'outstanding'},
        'gpt-3.5': {'params': 175e9, 'speed': 'slow', 'quality': 'outstanding'},
        't5-large': {'params': 770e6, 'speed': 'moderate', 'quality': 'outstanding'},
    }
    
    COMPLEXITY_THRESHOLDS = {
        'word_count': {
            'simple': 500,
            'moderate': 2000,
            'complex': 5000,
            'very_complex': float('inf')
        },
        'sentence_length': {
            'simple': 15,
            'moderate': 25,
            'complex': 40,
            'very_complex': float('inf')
        },
        'vocabulary_complexity': {
            'simple': 0.3,
            'moderate': 0.5,
            'complex': 0.7,
            'very_complex': 1.0
        }
    }
    
    def __init__(self):
        """Initialize model selector."""
        self.current_model = None
        self.current_complexity = None
        self.use_rag = False
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Analyze document to determine complexity.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with complexity analysis
        """
        words = text.split()
        sentences = text.split('.')
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        unique_words = len(set(w.lower() for w in words))
        vocabulary_richness = unique_words / max(word_count, 1)
        
        analysis = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'vocabulary_richness': vocabulary_richness,
        }
        
        return analysis
    
    def determine_complexity(self, analysis: Dict[str, Any]) -> DocumentComplexity:
        """
        Determine document complexity from analysis.
        
        Args:
            analysis: Document analysis dictionary
            
        Returns:
            DocumentComplexity enum
        """
        word_count = analysis['word_count']
        avg_sentence_length = analysis['avg_sentence_length']
        vocab_richness = analysis['vocabulary_richness']
        
        complexity_score = 0
        
        if word_count > self.COMPLEXITY_THRESHOLDS['word_count']['very_complex']:
            complexity_score += 3
        elif word_count > self.COMPLEXITY_THRESHOLDS['word_count']['complex']:
            complexity_score += 2.5
        elif word_count > self.COMPLEXITY_THRESHOLDS['word_count']['moderate']:
            complexity_score += 1.5
        elif word_count > self.COMPLEXITY_THRESHOLDS['word_count']['simple']:
            complexity_score += 0.5
        
        if avg_sentence_length > self.COMPLEXITY_THRESHOLDS['sentence_length']['very_complex']:
            complexity_score += 3
        elif avg_sentence_length > self.COMPLEXITY_THRESHOLDS['sentence_length']['complex']:
            complexity_score += 2.5
        elif avg_sentence_length > self.COMPLEXITY_THRESHOLDS['sentence_length']['moderate']:
            complexity_score += 1.5
        elif avg_sentence_length > self.COMPLEXITY_THRESHOLDS['sentence_length']['simple']:
            complexity_score += 0.5
        
        if vocab_richness > self.COMPLEXITY_THRESHOLDS['vocabulary_complexity']['very_complex']:
            complexity_score += 3
        elif vocab_richness > self.COMPLEXITY_THRESHOLDS['vocabulary_complexity']['complex']:
            complexity_score += 2.5
        elif vocab_richness > self.COMPLEXITY_THRESHOLDS['vocabulary_complexity']['moderate']:
            complexity_score += 1.5
        elif vocab_richness > self.COMPLEXITY_THRESHOLDS['vocabulary_complexity']['simple']:
            complexity_score += 0.5
        
        if complexity_score < 2:
            return DocumentComplexity.SIMPLE
        elif complexity_score < 4:
            return DocumentComplexity.MODERATE
        elif complexity_score < 6:
            return DocumentComplexity.COMPLEX
        else:
            return DocumentComplexity.VERY_COMPLEX
    
    def select_model(self, text: str, prefer_fast: bool = True) -> Dict[str, Any]:
        """
        Select best model based on document.
        
        Args:
            text: Document text
            prefer_fast: If True, prefer speed over quality
            
        Returns:
            Dictionary with model recommendation and settings
        """
        analysis = self.analyze_document(text)
        complexity = self.determine_complexity(analysis)
        
        self.current_complexity = complexity
        
        logger.info(f"Document complexity: {complexity.value}")
        logger.info(f"Analysis: word_count={analysis['word_count']}, "
                   f"avg_sentence_length={analysis['avg_sentence_length']:.1f}, "
                   f"vocabulary_richness={analysis['vocabulary_richness']:.2f}")
        
        if complexity == DocumentComplexity.SIMPLE:
            return self._get_lightweight_recommendation(prefer_fast)
        elif complexity == DocumentComplexity.MODERATE:
            return self._get_balanced_recommendation(prefer_fast)
        elif complexity == DocumentComplexity.COMPLEX:
            return self._get_advanced_recommendation(prefer_fast)
        else:
            return self._get_advanced_recommendation_with_rag(prefer_fast)
    
    def _get_lightweight_recommendation(self, prefer_fast: bool) -> Dict[str, Any]:
        """Recommend lightweight model for simple documents."""
        if prefer_fast:
            model = 't5-small'
        else:
            model = 'bart-base'
        
        return {
            'model': model,
            'category': ModelCategory.LIGHTWEIGHT,
            'use_rag': False,
            'num_beams': 2,
            'max_length': 100,
            'reason': 'Simple document - lightweight model sufficient',
            'estimated_time': '1-2 seconds'
        }
    
    def _get_balanced_recommendation(self, prefer_fast: bool) -> Dict[str, Any]:
        """Recommend balanced model for moderate complexity documents."""
        if prefer_fast:
            model = 't5-base'
        else:
            model = 'bart-large-cnn'
        
        return {
            'model': model,
            'category': ModelCategory.BALANCED,
            'use_rag': False,
            'num_beams': 4,
            'max_length': 150,
            'reason': 'Moderate complexity - balanced model recommended',
            'estimated_time': '2-5 seconds'
        }
    
    def _get_advanced_recommendation(self, prefer_fast: bool) -> Dict[str, Any]:
        """Recommend advanced model for complex documents."""
        if prefer_fast:
            model = 'pegasus-arxiv'
        else:
            model = 't5-large'
        
        return {
            'model': model,
            'category': ModelCategory.ADVANCED,
            'use_rag': True,
            'num_beams': 4,
            'max_length': 200,
            'reason': 'Complex document - advanced model with RAG recommended',
            'estimated_time': '3-7 seconds'
        }
    
    def _get_advanced_recommendation_with_rag(self, prefer_fast: bool) -> Dict[str, Any]:
        """Recommend advanced model with RAG for very complex documents."""
        return {
            'model': 't5-large',
            'category': ModelCategory.ADVANCED,
            'use_rag': True,
            'num_beams': 4,
            'max_length': 250,
            'reason': 'Very complex document - RAG pipeline required for context awareness',
            'estimated_time': '5-10 seconds',
            'retrieval_chunks': 5,
            'chunk_overlap': 100
        }
    
    def should_use_rag(self, complexity: DocumentComplexity) -> bool:
        """
        Determine if RAG should be used.
        
        Args:
            complexity: Document complexity
            
        Returns:
            Boolean indicating whether to use RAG
        """
        return complexity in [DocumentComplexity.COMPLEX, DocumentComplexity.VERY_COMPLEX]
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            model_name: Model name
            
        Returns:
            Model information or None if not found
        """
        for models_dict in [self.LIGHTWEIGHT_MODELS, self.BALANCED_MODELS, self.ADVANCED_MODELS]:
            if model_name in models_dict:
                return models_dict[model_name]
        
        return None
    
    def recommend_settings(self, text: str, quality_preference: str = 'balanced') -> Dict[str, Any]:
        """
        Get recommended settings for document summarization.
        
        Args:
            text: Document text
            quality_preference: 'speed', 'balanced', or 'quality'
            
        Returns:
            Recommended settings dictionary
        """
        prefer_fast = quality_preference == 'speed'
        recommendation = self.select_model(text, prefer_fast)
        
        model_info = self.get_model_info(recommendation['model'])
        if model_info:
            recommendation['model_info'] = model_info
        
        return recommendation
