"""
Text preprocessing and tokenization module for technical documents
"""

import re
import logging
from typing import List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Comprehensive text preprocessing for technical documents."""
    
    def __init__(self, remove_stopwords: bool = False):
        """
        Initialize preprocessor.
        
        Args:
            remove_stopwords: Whether to remove English stopwords
        """
        self.remove_stopwords = remove_stopwords
        self.stop_words = set(stopwords.words('english')) if remove_stopwords else set()
    
    def clean_text(self, text: str) -> str:
        """
        Clean technical document text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep punctuation for sentences
        text = re.sub(r'[^\w\s.!?,;:\-()]', '', text)
        
        # Remove extra spaces created by above operations
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_citations(self, text: str) -> str:
        """
        Remove citation references from text.
        
        Args:
            text: Text with citations
            
        Returns:
            Text without citations
        """
        # Remove [Author et al., Year] style citations
        text = re.sub(r'\[\d+\]|\[[\w\s\.]+,\s*\d{4}\]', '', text)
        
        # Remove (Author Year) style citations
        text = re.sub(r'\([\w\s\.]+,?\s*\d{4}\)', '', text)
        
        return text
    
    def remove_equations(self, text: str) -> str:
        """
        Remove mathematical equations and formulas.
        
        Args:
            text: Text with equations
            
        Returns:
            Text without equations
        """
        # Remove LaTeX equations
        text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
        text = re.sub(r'\$.*?\$', '', text)
        
        return text
    
    def sent_tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        sentences = sent_tokenize(text)
        return [sent.strip() for sent in sentences if sent.strip()]
    
    def word_tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        tokens = word_tokenize(text.lower())
        
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stop_words and t.isalnum()]
        
        return tokens
    
    def preprocess_document(self, text: str, remove_citations: bool = True,
                           remove_equations: bool = False) -> str:
        """
        Complete preprocessing pipeline.
        
        Args:
            text: Raw document text
            remove_citations: Whether to remove citations
            remove_equations: Whether to remove equations
            
        Returns:
            Preprocessed text
        """
        # Clean text
        text = self.clean_text(text)
        
        # Remove citations if requested
        if remove_citations:
            text = self.remove_citations(text)
        
        # Remove equations if requested
        if remove_equations:
            text = self.remove_equations(text)
        
        logger.info("Document preprocessing completed")
        return text


class TechnicalDocumentParser:
    """Parse technical document structure (sections, abstracts, etc.)."""
    
    @staticmethod
    def extract_abstract(text: str) -> Tuple[str, str]:
        """
        Extract abstract from document.
        
        Args:
            text: Full document text
            
        Returns:
            Tuple of (abstract, remaining_text)
        """
        abstract_match = re.search(
            r'(?:^|\n)(abstract|summary)(.*?)(?:\n(?:introduction|1\.|contents))',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if abstract_match:
            abstract = abstract_match.group(2).strip()
            remaining = text[:abstract_match.start()] + text[abstract_match.end():]
            return abstract, remaining
        
        return "", text
    
    @staticmethod
    def extract_sections(text: str) -> List[Tuple[str, str]]:
        """
        Extract document sections.
        
        Args:
            text: Document text
            
        Returns:
            List of (section_title, section_content) tuples
        """
        # Match common section patterns
        section_pattern = r'(?:^|\n)((?:\d+\.\s+)?(?:introduction|methodology|results|discussion|conclusion|references|abstract).*?)(?:\n(?:\d+\.\s+)?(?:[A-Z][^.]*?)(?=\n|$))'
        
        sections = []
        matches = re.finditer(section_pattern, text, re.IGNORECASE)
        
        for match in matches:
            title = match.group(1).strip()
            content = match.group(2).strip() if match.lastindex >= 2 else ""
            sections.append((title, content))
        
        return sections
