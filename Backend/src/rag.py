"""
Retrieval-Augmented Generation (RAG) pipeline for enhanced summarization
"""

import logging
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Intelligently chunk documents while preserving context."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 100, min_chunk_size: int = 100):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks for context preservation
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_document(self, text: str, preserve_sentences: bool = True) -> List[str]:
        """
        Intelligently chunk document.
        
        Args:
            text: Document text
            preserve_sentences: Keep sentences intact when chunking
            
        Returns:
            List of text chunks
        """
        if preserve_sentences:
            return self._chunk_by_sentences(text)
        else:
            return self._chunk_by_characters(text)
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk by sentence boundaries."""
        sentences = text.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            test_chunk = current_chunk + " " + sentence + "."
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk.strip()
            else:
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk)
                current_chunk = sentence + "."
        
        if len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_by_characters(self, text: str) -> List[str]:
        """Chunk by character count with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            if end < len(text):
                last_period = text.rfind('.', start, end)
                if last_period > start + self.min_chunk_size:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
            
            start = end - self.overlap
        
        return chunks


class EmbeddingGenerator:
    """Generate embeddings for text chunks."""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding generator.
        
        Args:
            model_name: HuggingFace model for embeddings (lightweight by default)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        self._load_model()
    
    def _load_model(self):
        """Load embedding model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text chunks
            batch_size: Batch size for processing
            
        Returns:
            Matrix of embeddings (num_texts, embedding_dim)
        """
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
        return np.array(embeddings)


class VectorDatabase:
    """FAISS-based vector database for fast retrieval."""
    
    def __init__(self, embedding_dim: int, index_type: str = 'flat'):
        """
        Initialize vector database.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of FAISS index ('flat' for exact, 'ivf' for approximate)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index = None
        self.chunks = []
        self._create_index()
    
    def _create_index(self):
        """Create FAISS index."""
        if self.index_type == 'flat':
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        elif self.index_type == 'ivf':
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        logger.info(f"Created FAISS index: {self.index_type}")
    
    def add_chunks(self, chunks: List[str], embeddings: np.ndarray):
        """
        Add chunks and their embeddings to database.
        
        Args:
            chunks: List of text chunks
            embeddings: Corresponding embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        self.chunks = chunks
        self.index.add(embeddings.astype(np.float32))
        logger.info(f"Added {len(chunks)} chunks to database")
    
    def retrieve(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[str], List[float]]:
        """
        Retrieve top-K most similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of chunks to retrieve
            
        Returns:
            Tuple of (retrieved_chunks, similarity_scores)
        """
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, min(k, len(self.chunks)))
        
        retrieved_chunks = [self.chunks[i] for i in indices[0]]
        similarities = [1 / (1 + d) for d in distances[0]]
        
        return retrieved_chunks, similarities


class RAGPipeline:
    """Complete RAG pipeline for context-aware summarization."""
    
    def __init__(
        self, 
        embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
        chunk_size: int = 512,
        overlap: int = 100
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Model for generating embeddings
            chunk_size: Size of document chunks
            overlap: Overlap between chunks
        """
        self.chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.vector_db = VectorDatabase(self.embedding_generator.embedding_dim)
        self.chunks = []
        self.embeddings = None
    
    def index_document(self, document: str) -> Dict[str, Any]:
        """
        Index a document for retrieval.
        
        Args:
            document: Document text
            
        Returns:
            Indexing statistics
        """
        logger.info("Starting document indexing")
        
        chunks = self.chunker.chunk_document(document)
        logger.info(f"Created {len(chunks)} chunks")
        
        embeddings = self.embedding_generator.generate_embeddings(chunks)
        self.vector_db.add_chunks(chunks, embeddings)
        
        self.chunks = chunks
        self.embeddings = embeddings
        
        return {
            'num_chunks': len(chunks),
            'embedding_dimension': self.embedding_generator.embedding_dim,
            'avg_chunk_length': np.mean([len(c) for c in chunks])
        }
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Query text
            k: Number of chunks to retrieve
            
        Returns:
            List of (chunk, relevance_score) tuples
        """
        query_embedding = self.embedding_generator.model.encode([query])[0]
        chunks, scores = self.vector_db.retrieve(query_embedding, k)
        
        return list(zip(chunks, scores))
    
    def merge_context(self, chunks: List[str], weights: Optional[List[float]] = None) -> str:
        """
        Merge retrieved chunks while preserving context.
        
        Args:
            chunks: List of retrieved chunks
            weights: Optional importance weights for each chunk
            
        Returns:
            Merged context text
        """
        if not chunks:
            return ""
        
        if weights is None:
            weights = [1.0] * len(chunks)
        
        weighted_chunks = []
        for chunk, weight in zip(chunks, weights):
            weight_factor = int(weight * 10)
            weighted_chunks.extend([chunk] * max(1, weight_factor))
        
        merged = " ".join(chunks)
        return merged.strip()


class ContextPreserver:
    """Preserve important context from retrieved chunks."""
    
    IMPORTANT_PATTERNS = {
        'method': ['method', 'approach', 'technique', 'algorithm', 'framework'],
        'metric': ['metric', 'accuracy', 'precision', 'recall', 'f1', 'score', 'performance'],
        'dataset': ['dataset', 'corpus', 'benchmark', 'collection'],
        'result': ['result', 'finding', 'conclusion', 'achieve', 'outperform'],
        'baseline': ['baseline', 'sota', 'state-of-the-art', 'previous work'],
    }
    
    @classmethod
    def extract_important_sentences(cls, text: str, category: Optional[str] = None) -> List[str]:
        """
        Extract important sentences from text.
        
        Args:
            text: Text to analyze
            category: Optional category to focus on
            
        Returns:
            List of important sentences
        """
        sentences = text.split('.')
        important = []
        
        patterns = cls.IMPORTANT_PATTERNS.get(category, [])
        if category:
            patterns = cls.IMPORTANT_PATTERNS.get(category, [])
        else:
            patterns = []
            for p_list in cls.IMPORTANT_PATTERNS.values():
                patterns.extend(p_list)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            if any(pattern in sentence.lower() for pattern in patterns):
                important.append(sentence + ".")
        
        return important
    
    @classmethod
    def assign_importance_scores(cls, sentences: List[str]) -> List[float]:
        """
        Assign importance scores to sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of importance scores (0-1)
        """
        scores = []
        
        for sentence in sentences:
            score = 0.3
            
            sentence_lower = sentence.lower()
            for category, patterns in cls.IMPORTANT_PATTERNS.items():
                if any(p in sentence_lower for p in patterns):
                    score += 0.2
            
            score = min(score, 1.0)
            scores.append(score)
        
        return scores
