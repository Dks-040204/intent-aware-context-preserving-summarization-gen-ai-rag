import logging
from typing import Optional, List, Dict, Any
import torch
from .preprocessing import TextPreprocessor, TechnicalDocumentParser
from .models import SummarizationModelLoader, IntentClassifier, ContextPreserver
from .utils import chunk_text
from .evaluation import SummaryEvaluator
from .keywords import KeywordExtractor
from .exporters import SummaryExporter
from .rag import RAGPipeline, ContextPreserver as RAGContextPreserver
from .model_selector import ModelSelector


logger = logging.getLogger(__name__)


class TechnicalDocumentSummarizer:
    """Main summarization pipeline for technical documents with language support."""
    
    def __init__(self, model_name: str = 't5-small', device: Optional[str] = None, language: str = None):
        """
        Initialize the summarizer.
        
        Args:
            model_name: Name of the model to use (default: t5-small for speed)
            device: Device to run on ('cpu' or 'cuda')
            language: Language for summarization (defaults to english if not provided)
        """
        # Only prompt for language if running interactively and language not provided
        if language is None:
            import sys
            if sys.stdin.isatty():  # Check if running in interactive terminal
                print("\n=== LANGUAGE SELECTION ===")
                print("Supported languages: english, spanish, french, german, italian,")
                print("portuguese, chinese, japanese, korean, arabic, hindi, russian, turkish, vietnamese, thai")
                language = input("\nEnter desired language for summarization (default: english): ").strip() or 'english'
            else:
                language = 'english'  # Default to English in non-interactive mode
        
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.language = language
        
        self.preprocessor = TextPreprocessor(remove_stopwords=False)
        self.parser = TechnicalDocumentParser()
        self.model_loader = SummarizationModelLoader(model_name, self.device, language)
        self.intent_classifier = IntentClassifier()
        self.context_preserver = ContextPreserver()
        
        self.model, self.tokenizer = self.model_loader.load_model()
        
        self.evaluator = SummaryEvaluator()
        self.keyword_extractor = KeywordExtractor()
        self.exporter = SummaryExporter()
        self.rag_pipeline = RAGPipeline()
        self.model_selector = ModelSelector()
        
        self.model_cache = {}
        
        logger.info(f"Summarizer initialized with {model_name} for {language}")
    
    def auto_summarize(
        self,
        document: str,
        intent: str = 'technical_overview',
        quality_preference: str = 'balanced',
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically select best model and summarize.
        
        Args:
            document: Document text
            intent: Summarization intent
            quality_preference: 'speed', 'balanced', or 'quality'
            language: Language for summarization
            
        Returns:
            Dictionary with summary and model selection info
        """
        recommendation = self.model_selector.recommend_settings(document, quality_preference)
        
        logger.info(f"Model selection: {recommendation['model']}")
        logger.info(f"Reason: {recommendation['reason']}")
        logger.info(f"Estimated time: {recommendation['estimated_time']}")
        
        use_rag = recommendation.get('use_rag', False)
        num_beams = recommendation.get('num_beams', 2)
        max_length = recommendation.get('max_length', 150)
        
        summary = self.summarize(
            document,
            intent=intent,
            max_length=max_length,
            num_beams=num_beams,
            language=language,
            use_rag=use_rag
        )
        
        return {
            'summary': summary,
            'model': recommendation['model'],
            'complexity': str(self.model_selector.current_complexity),
            'use_rag': use_rag,
            'estimated_time': recommendation['estimated_time'],
            'reason': recommendation['reason']
        }
    
    def summarize(
        self, 
        document: str,
        intent: str = 'technical_overview',
        max_length: int = 150,
        min_length: int = 50,
        num_beams: int = 2,
        language: Optional[str] = None,
        use_rag: bool = False,
    ) -> str:
        """
        Summarize a technical document in simple language.
        
        Args:
            document: Document text to summarize (supports long papers)
            intent: Summarization intent/style
            max_length: Maximum length of summary (default: 150 tokens)
            min_length: Minimum length of summary
            num_beams: Number of beams for beam search (default: 2 for speed)
            language: Override language for this summary
            use_rag: Use RAG pipeline for context retrieval
            
        Returns:
            Simplified summary text
        """
        if language and language != self.language:
            self.model_loader.language = language
            self.model_loader.language_code = self.model_loader.SUPPORTED_LANGUAGES.get(language.lower(), 'en_XX')
            if hasattr(self.tokenizer, 'src_lang'):
                self.tokenizer.src_lang = self.model_loader.language_code
        
        if isinstance(intent, str):
            intent = self.intent_classifier.classify_intent(intent)
        
        cleaned_text = self.preprocessor.preprocess_document(
            document,
            remove_citations=True,
            remove_equations=False
        )
        
        abstract, remaining = self.parser.extract_abstract(cleaned_text)
        
        if use_rag:
            indexing_stats = self.rag_pipeline.index_document(cleaned_text)
            logger.info(f"Indexed document: {indexing_stats}")
            
            intent_prompt = self.intent_classifier.get_prompt_for_intent(intent)
            retrieved_chunks = self.rag_pipeline.retrieve_context(intent_prompt, k=3)
            summary_text = self.rag_pipeline.merge_context(
                [chunk for chunk, _ in retrieved_chunks],
                [score for _, score in retrieved_chunks]
            )
        else:
            summary_text = self._prepare_for_summarization(
                abstract, 
                remaining, 
                max_length
            )
        
        summary = self._generate_summary(
            summary_text,
            intent,
            max_length,
            min_length,
            num_beams
        )
        
        summary = self._simplify_language(summary)
        
        return summary
    
    def _prepare_for_summarization(
        self, 
        abstract: str, 
        text: str,
        max_length: int
    ) -> str:
        """
        Prepare text for summarization, handling long documents.
        
        Args:
            abstract: Document abstract if available
            text: Main document text
            max_length: Target max length
            
        Returns:
            Prepared text for summarization
        """
        prepared = abstract if abstract else ""
        
        max_tokens = 512 * 2
        
        if len(text) > 4000:
            chunks = chunk_text(text, chunk_size=1000, overlap=100)
            prepared += " ".join(chunks[:2])
        else:
            prepared += " " + text
        
        return prepared.strip()
    
    def _generate_summary(
        self,
        text: str,
        intent: str,
        max_length: int,
        min_length: int,
        num_beams: int
    ) -> str:
        """
        Generate summary text (optimized for speed).
        
        Args:
            text: Text to summarize
            intent: Intent for summarization
            max_length: Maximum summary length
            min_length: Minimum summary length
            num_beams: Number of beams
            
        Returns:
            Generated summary
        """
        intent_prefix = self.intent_classifier.get_prompt_for_intent(intent)
        input_text = f"summarize: {intent_prefix}: {text}"
        
        inputs = self.tokenizer(
            input_text,
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding='max_length'
        ).to(self.device)
        
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                max_length=max_length,
                min_length=min_length,
                num_beams=num_beams,
                early_stopping=True,
                do_sample=False,
                temperature=1.0,
            )
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        logger.info(f"Summary generated with intent: {intent} in {self.language}")
        return summary
    def _simplify_language(self, text: str) -> str:
        """
        Simplify language to make summary easy to understand.
        
        Args:
            text: Text to simplify
            
        Returns:
            Simplified text
        """
        simplifications = {
            'utilize': 'use',
            'demonstrate': 'show',
            'implement': 'create',
            'facilitate': 'help',
            'novel': 'new',
            'proposed': 'suggested',
            'efficacy': 'effectiveness',
            'robust': 'strong',
            'comprehensive': 'complete',
            'subsequent': 'next',
            'aforementioned': 'mentioned',
            'henceforth': 'from now on',
        }
        
        simplified = text
        for complex_word, simple_word in simplifications.items():
            import re
            simplified = re.sub(
                r'\b' + complex_word + r'\b',
                simple_word,
                simplified,
                flags=re.IGNORECASE
            )
        
        import re
        sentences = re.split(r'(?<=[.!?])\s+', simplified)
        simplified_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 120:  # Split very long sentences
                parts = sentence.split(' and ')
                if len(parts) > 1:
                    simplified_sentences.extend(parts)
                else:
                    simplified_sentences.append(sentence)
            else:
                simplified_sentences.append(sentence)
        
        return ' '.join(simplified_sentences)
    
    def summarize_batch(
        self,
        documents: List[str],
        intent: str = 'technical_overview',
        language: Optional[str] = None,
        return_keywords: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Summarize multiple documents efficiently (batch processing).
        
        Args:
            documents: List of documents to summarize
            intent: Summarization intent
            language: Language for summarization
            return_keywords: Extract keywords for each
            
        Returns:
            List of summary results
        """
        logger.info(f"Batch summarizing {len(documents)} documents...")
        results = []
        
        for i, doc in enumerate(documents, 1):
            try:
                result = self.summarize(
                    doc,
                    intent=intent,
                    language=language
                )
                results.append(result)
                logger.info(f"Processed {i}/{len(documents)}")
            except Exception as e:
                logger.error(f"Error processing document {i}: {str(e)}")
                results.append({'error': str(e)})
        
        logger.info(f"Batch summarization complete")
        return results
    
    def _format_as_bullets(self, summary: str) -> str:
        """
        Format summary as bullet points.
        
        Args:
            summary: Summary text
            
        Returns:
            Formatted as bullets
        """
        sentences = summary.split('.')
        bullets = [f"• {s.strip()}" for s in sentences if s.strip()]
        return '\n'.join(bullets)
    
    def summarize_with_sections(
        self, 
        document: str,
        max_length_per_section: int = 100
    ) -> Dict[str, str]:
        """
        Summarize document with separate summaries for each section.
        
        Args:
            document: Document text
            max_length_per_section: Max length for each section summary
            
        Returns:
            Dictionary of section summaries
        """
        sections = self.parser.extract_sections(document)
        summaries = {}
        
        for section_title, section_content in sections:
            if section_content.strip():
                summary = self.summarize(
                    section_content,
                    max_length=max_length_per_section
                )
                summaries[section_title] = summary
        
        return summaries
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return self.model_loader.get_model_info()
