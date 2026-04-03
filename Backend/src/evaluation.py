"""
Quality metrics and evaluation for summaries
"""

import logging
from typing import Dict, Tuple
from rouge_score import rouge_scorer
import torch

logger = logging.getLogger(__name__)


class SummaryEvaluator:
    """Evaluate summary quality using ROUGE scores and confidence metrics."""
    
    def __init__(self):
        """Initialize evaluator with ROUGE scorer."""
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
    
    def calculate_rouge_scores(
        self, 
        summary: str, 
        reference: str = None
    ) -> Dict[str, float]:
        """
        Calculate ROUGE scores (optional reference).
        
        Args:
            summary: Generated summary
            reference: Reference summary (optional)
            
        Returns:
            Dictionary with ROUGE scores
        """
        if not reference:
            # Self-evaluation based on length and complexity
            words = summary.split()
            unique_words = len(set(words))
            avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
            
            # Simple heuristics
            return {
                'length_score': min(len(words) / 150, 1.0),
                'diversity_score': unique_words / len(words) if words else 0,
                'complexity_score': min(avg_word_length / 6, 1.0)
            }
        
        # Calculate ROUGE against reference
        scores = self.rouge_scorer.score(reference, summary)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def get_confidence_score(
        self, 
        model_output: torch.Tensor,
        summary: str
    ) -> float:
        """
        Calculate confidence score (0-1).
        
        Args:
            model_output: Raw model output logits
            summary: Generated summary
            
        Returns:
            Confidence score (0-1)
        """
        # Based on model probabilities and summary length
        if hasattr(model_output, 'sequences_scores'):
            scores = model_output.sequences_scores
            confidence = torch.sigmoid(scores).item() if len(scores) > 0 else 0.5
        else:
            confidence = 0.5
        
        # Adjust based on summary characteristics
        words = summary.split()
        if 5 <= len(words) <= 200:  # Reasonable length
            confidence *= 1.1
        
        return min(confidence, 1.0)
    
    def evaluate_summary(
        self,
        summary: str,
        reference: str = None,
        model_output: torch.Tensor = None
    ) -> Dict[str, any]:
        """
        Complete evaluation of summary.
        
        Args:
            summary: Generated summary
            reference: Reference summary
            model_output: Model output for confidence
            
        Returns:
            Comprehensive evaluation metrics
        """
        rouge_scores = self.calculate_rouge_scores(summary, reference)
        confidence = self.get_confidence_score(model_output, summary)
        
        return {
            'summary': summary,
            'rouge_scores': rouge_scores,
            'confidence_score': confidence,
            'length': len(summary.split()),
            'quality': 'high' if confidence > 0.7 else 'medium' if confidence > 0.5 else 'low'
        }
