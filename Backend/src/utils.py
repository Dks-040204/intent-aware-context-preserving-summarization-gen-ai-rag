import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return {}


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    logger.info(f"Configuration saved to {config_path}")


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between consecutive chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    step = chunk_size - overlap
    
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if len(chunk) > 0:
            chunks.append(chunk)
    
    logger.info(f"Text split into {len(chunks)} chunks")
    return chunks


def merge_chunks(chunks: List[str], overlap: int = 50) -> str:
    """
    Merge overlapping text chunks back into single text.
    
    Args:
        chunks: List of text chunks
        overlap: Original overlap size
        
    Returns:
        Merged text
    """
    if not chunks:
        return ""
    
    merged = chunks[0]
    for chunk in chunks[1:]:
        # Remove overlapping portion
        merged += chunk[overlap:]
    
    return merged


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def count_tokens_approximate(text: str) -> int:
    """
    Approximate token count using word-based heuristic.
    For more accurate counting, use tokenizer from transformers library.
    
    Args:
        text: Input text
        
    Returns:
        Approximate token count
    """
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4
