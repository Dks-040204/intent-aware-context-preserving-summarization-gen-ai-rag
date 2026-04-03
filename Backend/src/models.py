"""
Model architectures and configurations for summarization
"""

import logging
from typing import Optional, List
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    pipeline
)


logger = logging.getLogger(__name__)


class SummarizationModelLoader:
    """Load and manage pre-trained summarization models."""
    
    # Popular pre-trained models for summarization
    AVAILABLE_MODELS = {
        # Fast & Lightweight models (RECOMMENDED)
        't5-small': 'google-t5/t5-small',
        't5-base': 'google-t5/t5-base',
        't5-large': 'google-t5/t5-large',
        'bart-base': 'facebook/bart-base',
        'bart-large-cnn': 'facebook/bart-large-cnn',
        'pegasus-arxiv': 'google/pegasus-arxiv',
        'pegasus-pubmed': 'google/pegasus-pubmed',
        'led': 'allenai/led-base-16384',  # For long documents
        
        # Multilingual models (supports 50+ languages)
        'mbart-50': 'facebook/mbart-large-50',
        'mbart-50-small': 'facebook/mbart-large-50-small',  # FASTEST - recommended for speed
        'mt5-small': 'google/mt5-small',  # Multilingual T5 (100+ languages)
        'mt5-base': 'google/mt5-base',
    }
    
    # Supported languages for multilingual models
    SUPPORTED_LANGUAGES = {
        'english': 'en_XX',
        'spanish': 'es_XX',
        'french': 'fr_XX',
        'german': 'de_DE',
        'italian': 'it_IT',
        'portuguese': 'pt_XX',
        'chinese': 'zh_CN',
        'japanese': 'ja_XX',
        'korean': 'ko_KR',
        'arabic': 'ar_AR',
        'hindi': 'hi_IN',
        'russian': 'ru_RU',
        'turkish': 'tr_TR',
        'vietnamese': 'vi_VN',
        'thai': 'th_TH',
    }
    
    def __init__(self, model_name: str = 't5-small', device: Optional[str] = None, language: str = 'english'):
        """
        Initialize model loader.
        
        Args:
            model_name: Name of the model to load (default: t5-small for speed)
            device: Device to load model on ('cpu' or 'cuda')
            language: Language for multilingual models
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.language = language
        self.language_code = self.SUPPORTED_LANGUAGES.get(language.lower(), 'en_XX')
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Using device: {self.device}")
        logger.info(f"Language: {language} (code: {self.language_code})")
    
    def load_model(self, model_path: Optional[str] = None) -> tuple:
        """
        Load model and tokenizer.
        
        Args:
            model_path: Path to local model or HuggingFace model ID
            
        Returns:
            Tuple of (model, tokenizer)
        """
        path = model_path or self.AVAILABLE_MODELS.get(self.model_name, self.model_name)
        
        try:
            logger.info(f"Loading tokenizer from {path}")
            self.tokenizer = AutoTokenizer.from_pretrained(path, use_fast=True)  # Fast tokenizer
            
            # Set language for multilingual models
            if 'mbart' in path.lower() or 'mt5' in path.lower():
                self.tokenizer.src_lang = self.language_code
            
            logger.info(f"Loading model from {path}")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(path)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully on {self.device}")
            return self.model, self.tokenizer
        
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_model_info(self) -> dict:
        """Get information about loaded model."""
        if self.model is None:
            return {"status": "Model not loaded"}
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }


class IntentClassifier:
    """Classify user intent for summarization."""
    
    INTENT_TYPES = {
        'technical_overview': 'high-level technical summary',
        'detailed_analysis': 'comprehensive technical analysis',
        'methodology': 'focus on methods and approach',
        'results': 'focus on results and findings',
        'conclusion': 'focus on conclusions and implications',
        'abstract': 'paper abstract-like summary',
    }
    
    def __init__(self):
        """Initialize intent classifier."""
        self.intent_prompts = {}
        for intent_key, intent_desc in self.INTENT_TYPES.items():
            self.intent_prompts[intent_key] = f"Provide {intent_desc}"
    
    def classify_intent(self, user_input: str) -> str:
        """
        Classify user intent from input text.
        
        Args:
            user_input: User's intent description
            
        Returns:
            Classified intent type
        """
        user_input_lower = user_input.lower()
        
        # Simple keyword matching (can be enhanced with ML model)
        for intent_key in self.INTENT_TYPES.keys():
            if intent_key.replace('_', ' ') in user_input_lower:
                return intent_key
        
        # Default to technical_overview
        return 'technical_overview'
    
    def get_prompt_for_intent(self, intent: str) -> str:
        """Get customized prompt for specific intent."""
        return self.intent_prompts.get(intent, self.intent_prompts['technical_overview'])


class ContextPreserver:
    """Preserve important context during summarization."""
    
    def __init__(self):
        """Initialize context preserver."""
        self.important_patterns = {
            'method': r'(?:method|approach|technique|algorithm)',
            'metric': r'(?:metric|accuracy|precision|recall|f1|score)',
            'dataset': r'(?:dataset|corpus|benchmark)',
            'baseline': r'(?:baseline|state-of-the-art|sota)',
        }
    
    def extract_important_content(self, text: str) -> List[str]:
        """
        Extract important content that should be preserved.
        
        Args:
            text: Document text
            
        Returns:
            List of important content snippets
        """
        important_snippets = []
        sentences = text.split('.')
        
        for sentence in sentences:
            for pattern in self.important_patterns.values():
                if len(sentence) > 20:  # Skip very short sentences
                    important_snippets.append(sentence.strip())
                    break
        
        return important_snippets
    
    def weight_content(self, sentences: List[str]) -> List[float]:
        """
        Assign importance weights to sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of importance weights
        """
        weights = []
        for sentence in sentences:
            weight = 1.0
            
            # Boost weight for important content
            for pattern in self.important_patterns.values():
                if any(word in sentence.lower() for word in pattern.split('|')):
                    weight += 0.5
            
            weights.append(min(weight, 2.0))  # Cap at 2.0
        
        return weights
