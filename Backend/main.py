import logging
import argparse
from pathlib import Path
from src.summarizer import TechnicalDocumentSummarizer
from src.exporters import SummaryExporter
from src.keywords import KeywordExtractor
from src.api import run_api
from src.web_ui import run_ui
from src.evaluation import SummaryEvaluator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def single_document_mode():
    logger.info("Starting Single Document Mode")
    
    summarizer = TechnicalDocumentSummarizer()
    exporter = SummaryExporter()
    keyword_extractor = KeywordExtractor()
    evaluator = SummaryEvaluator()
    
    # Get document path
    doc_path = input("\nEnter document path (or paste text): ").strip()
    
    # Load document
    if Path(doc_path).exists():
        with open(doc_path, 'r', encoding='utf-8') as f:
            document = f.read()
        logger.info(f"Loaded document from {doc_path}")
    else:
        document = doc_path
    
    # Get options
    intent = input("Summary intent (technical_overview/methodology/results/conclusion): ").strip() or 'technical_overview'
    quality_pref = input("Quality preference (speed/balanced/quality): ").strip() or 'balanced'
    
    # Summarize with auto_summarize for intelligent model selection
    logger.info("Analyzing document and generating summary...")
    result = summarizer.auto_summarize(
        document=document,
        intent=intent,
        quality_preference=quality_pref
    )
    
    summary = result.get('summary', result) if isinstance(result, dict) else result
    
    # Extract keywords
    keywords_dict = keyword_extractor.extract_all(summary, keywords_k=5, phrases_k=3)
    
    # Evaluate summary
    evaluation = evaluator.evaluate_summary(summary)
    
    # Display results
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(summary)
    
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    print(f"📊 Model Used: {result.get('model', 'auto') if isinstance(result, dict) else 'auto'}")
    print(f"📈 Complexity: {result.get('complexity', 'unknown') if isinstance(result, dict) else 'unknown'}")
    print(f"🔧 Used RAG: {result.get('use_rag', False) if isinstance(result, dict) else False}")
    print(f"⏱️ Time: {result.get('estimated_time', 'N/A') if isinstance(result, dict) else 'N/A'}")
    
    print("\n" + "="*80)
    print("KEYWORDS & PHRASES")
    print("="*80)
    if keywords_dict.get('keywords'):
        print(f"Keywords: {', '.join(keywords_dict['keywords'])}")
    if keywords_dict.get('key_phrases'):
        print(f"Key Phrases: {', '.join(keywords_dict['key_phrases'])}")
    
    print("\n" + "="*80)
    print("QUALITY METRICS")
    print("="*80)
    print(f"✅ Quality: {evaluation.get('quality', 'Medium')}")
    print(f"📝 Length: {evaluation.get('length', 0)} words")
    print(f"💯 Confidence: {evaluation.get('confidence_score', 0):.2f}")
    
    # Export
    export_format = input("\nExport format (json/txt/pdf/md): ").strip() or 'txt'
    if export_format in ['json', 'txt', 'pdf', 'md']:
        export_method = getattr(exporter, f'export_{export_format}')
        filepath = export_method(summary, title="Document Summary")
        logger.info(f"✅ Exported to {filepath}")


def batch_mode():
    """Batch processing mode."""
    logger.info("Starting Batch Mode")
    
    summarizer = TechnicalDocumentSummarizer()
    exporter = SummaryExporter()
    
    # Get directory
    directory = input("\nEnter directory with documents: ").strip()
    path = Path(directory)
    
    if not path.exists():
        logger.error("❌ Directory not found")
        return
    
    # Get documents
    files = list(path.glob('*.txt')) + list(path.glob('*.pdf'))
    logger.info(f"Found {len(files)} documents")
    
    if len(files) == 0:
        logger.warning("No TXT or PDF files found")
        return
    
    documents = []
    file_names = []
    for file in files:
        try:
            if file.suffix == '.pdf':
                logger.info(f"Skipping PDF (install pdfplumber for PDF support): {file.name}")
                continue
            with open(file, 'r', encoding='utf-8') as f:
                documents.append(f.read())
            file_names.append(file.name)
        except Exception as e:
            logger.error(f"Error reading {file.name}: {str(e)}")
    
    if not documents:
        logger.error("No documents could be loaded")
        return
    
    intent = input("Summary intent (technical_overview/methodology/results/conclusion): ").strip() or 'technical_overview'
    quality_pref = input("Quality preference (speed/balanced/quality): ").strip() or 'balanced'
    
    # Batch summarize
    logger.info(f"Processing {len(documents)} documents...")
    results = summarizer.summarize_batch(documents, intent=intent, language='english')
    
    # Create results dictionary
    summaries = {}
    for i, (fname, result) in enumerate(zip(file_names, results)):
        if isinstance(result, dict) and 'error' in result:
            summaries[fname] = f"Error: {result['error']}"
        else:
            summaries[fname] = result
        logger.info(f"✅ Processed {i+1}/{len(documents)}: {fname}")
    
    # Export
    export_format = input("Export format (json/txt): ").strip() or 'json'
    if export_format == 'json':
        filepath = exporter.export_json(
            summary=summaries,
            metadata={"total_documents": len(documents), "intent": intent, "quality": quality_pref},
            filename=f"batch_summaries_{len(documents)}_docs.json"
        )
    else:
        # Export as text
        text_summary = "\n\n".join([f"# {fname}\n{summary}" for fname, summary in summaries.items()])
        filepath = exporter.export_text(text_summary, filename=f"batch_summaries_{len(documents)}_docs.txt")
    
    logger.info(f"✅ Exported {len(results)} summaries to {filepath}")


def api_mode():
    logger.info("Starting REST API Server")
    host = input("API Host (default 0.0.0.0): ").strip() or "0.0.0.0"
    port = int(input("API Port (default 8000): ").strip() or "8000")
    
    logger.info(f"API running at http://{host}:{port}")
    logger.info("API docs available at http://{host}:{port}/docs")
    
    run_api(host=host, port=port)


def web_ui_mode():
    logger.info("Starting Web UI")
    host = input("UI Host (default 0.0.0.0): ").strip() or "0.0.0.0"
    port = int(input("UI Port (default 8001): ").strip() or "8001")
    
    logger.info(f"Web UI running at http://{host}:{port}")
    
    run_ui(host=host, port=port)


def main():
    print("\n" + "="*80)
    print("INTENT-AWARE DOCUMENT SUMMARIZER")
    print("="*80)
    print("\nStarting REST API Server with Uvicorn...")
    
    # Auto-run API mode with default values
    run_api(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
