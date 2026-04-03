# 🚀 Intent-Aware Context-Preserving Summarization System

**Advanced AI-powered summarization system for technical documents using Transformers, RAG, and intelligent model selection**

---

## 📊 Project Status & Badges

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Latest-red)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

### 🎯 What This Project Does

Transform lengthy technical documents into concise, intelligent summaries while preserving critical context. Our system understands **user intent** and automatically selects the best AI model based on document complexity, ensuring optimal speed-to-quality tradeoffs.

**Perfect for:**
- 📄 Academic papers (arXiv, PubMed)
- 🔬 Research documents
- 📊 Technical specifications
- 📚 Scientific publications
- 📋 Long-form technical content

### ⚡ Key Highlights

- **15 Language Support** - Works with documents in 15 different languages
- **6 Summarization Intents** - Customize summaries for different purposes (overview, analysis, methodology, results, conclusion, abstract)
- **3 Quality Modes** - Speed (⚡ <2s), Balanced (⚖️ 2-5s), Quality (✨ 5-10s)
- **REST API + Web UI** - Choose between command-line, API, or professional web interface
- **Smart Model Selection** - Automatically picks optimal model (T5-Small/Base/Large, Pegasus) based on document complexity
- **RAG Pipeline** - Uses vector embeddings & semantic search for enhanced summaries on complex documents
- **Quality Metrics** - Evaluates summaries with ROUGE scores, confidence scoring, and keyword extraction
- **Multiple Export Formats** - JSON (with metadata), PDF (formatted), TXT (plain), Markdown

---

## ✨ Project Overview

This is a production-ready document summarization system that:
- ✅ Intelligently selects best model based on document complexity
- ✅ Supports 15 languages and 6 summarization intents
- ✅ Uses RAG (Retrieval-Augmented Generation) for complex documents
- ✅ Provides REST API & Web UI with real-time progress
- ✅ Exports results in JSON, PDF, TXT, and Markdown formats
- ✅ Evaluates quality with ROUGE scores & confidence metrics
- ✅ Extracts keywords and technical terms automatically

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **Intelligent Model Selection** | Auto-detects document complexity → chooses optimal model |
| **RAG Pipeline** | Vector embeddings + semantic search for enhanced summaries |
| **Multi-Language Support** | English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, Russian, Turkish, Vietnamese, Thai |
| **Summarization Intents** | 6 types: technical_overview, detailed_analysis, methodology, results, conclusion, abstract |
| **Quality Modes** | Speed (⚡ <2s), Balanced (⚖️ 2-5s), Quality (✨ 5-10s) |
| **REST API** | FastAPI with 5 endpoints + Swagger docs |
| **Web UI** | Professional interface with sidebar, tabs, history, settings |
| **Batch Processing** | Process multiple documents at once |
| **Export Formats** | JSON (metadata), PDF (formatted), TXT (plain), Markdown |
| **Evaluation Metrics** | ROUGE-1/2/L scores, confidence scoring, keyword extraction |

## 📁 Project Structure

```
Backend/
├── 🎯 main.py                         ⭐ Entry point (4 operation modes)
├── ⚙️ config.json                      Configuration & model settings
├── 📋 requirements.txt                All dependencies
├── 📖 README.md                       This file
├── 📚 SYSTEM_DOCUMENTATION.md         ⭐ DETAILED ARCHITECTURE GUIDE
├── 📮 Postman_Collection.json         API test suite (7 tests)
├── src/                               Core modules (13 files)
│   ├── summarizer.py (390 lines)      Main orchestrator
│   ├── api.py (220 lines)             FastAPI REST endpoints
│   ├── web_ui.py (1148 lines)         Web interface (HTML/CSS/JS)
│   ├── preprocessing.py               Text cleaning & tokenization
│   ├── model_selector.py (299 lines)  Complexity analysis & routing
│   ├── rag.py (360 lines)             Vector embeddings & search
│   ├── models.py                      Model loading & management
│   ├── evaluation.py                  ROUGE scores & quality metrics
│   ├── keywords.py                    Keyword extraction
│   ├── exporters.py                   JSON/PDF/TXT export
│   ├── fine_tuner.py                  Model fine-tuning utilities
│   ├── utils.py                       Helper functions
│   └── __init__.py                    Package initialization
├── data/                              Raw & processed data samples
├── models/                            Model checkpoints & tokenizers
├── notebooks/                         Jupyter notebooks for experiments
└── results/                           Output summaries & evaluations
```

## 🏗️ System Architecture

```
INPUT LAYER          PROCESSING          ANALYSIS              MODELS           OUTPUT
┌──────────────┐    ┌──────────────┐   ┌──────────────┐     ┌──────────────┐  ┌──────────────┐
│ Text Input   │    │ Clean Text   │   │ Detect       │     │ T5-Small     │  │ JSON Export  │
│ File Upload  │───→│ Tokenize     │───→│ Complexity   │────→│ T5-Base      │─→│ PDF Report   │
│ Batch Files  │    │ Chunk (512)  │   │ Select Model │     │ T5-Large     │  │ TXT/Markdown │
└──────────────┘    │ (w/ overlap) │   │ RAG Decision │     │ Pegasus+RAG  │  └──────────────┘
                    └──────────────┘   └──────────────┘     └──────────────┘
                          ↓                    ↓                     ↓
                    EVALUATION LAYER    QUALITY METRICS      KEYWORD EXTRACTION
                    ROUGE Scores        Confidence Scores    Technical Terms
```

## 🚀 Quick Start (4 Operation Modes)

### Installation
```bash
# 1. Navigate to Backend folder
cd Backend

# 2. Create virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\activate          # Windows
source .venv/bin/activate         # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Mode 1️⃣ - Single Document Summarization
```bash
python main.py
# Select: 1
# Paste or upload document → Get summary
```

### Mode 2️⃣ - Batch Processing
```bash
python main.py
# Select: 2
# Upload multiple files → Process all at once
```

### Mode 3️⃣ - REST API Server
```bash
python main.py
# Select: 3
# API runs on http://localhost:8000
# Import Postman_Collection.json for testing
# View interactive docs at http://localhost:8000/docs
```

### Mode 4️⃣ - Web UI
```bash
python main.py
# Select: 4
# Open http://localhost:8001 in browser
# Professional interface with history & settings
```

## 📖 Detailed Documentation

For complete architecture details, module descriptions, and advanced usage:
👉 **See [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)** for:
- 13 detailed module documentation
- System architecture diagrams
- Component interactions & workflows
- Performance characteristics
- Development & testing guide

## 🔌 API Reference

### REST Endpoints

**Base URL:** `http://localhost:8000` (when running Mode 3)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server status check |
| `/languages` | GET | List supported languages (15) |
| `/intents` | GET | List summarization intents (6) |
| `/summarize` | POST | Summarize single document |
| `/batch-summarize` | POST | Process multiple documents |
| `/docs` | GET | Interactive API documentation (Swagger) |

### Example: Summarize API Call
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "Your document text here...",
    "language": "english",
    "intent": "technical_overview",
    "quality_preference": "balanced"
  }'
```

### Response Example
```json
{
  "summary": "AI systems learn from data patterns...",
  "language": "english",
  "intent": "technical_overview",
  "length": 45,
  "model": "t5-base",
  "complexity": "MODERATE",
  "use_rag": false,
  "confidence_score": 0.92,
  "keywords": ["machine learning", "neural networks", "training"],
  "rouge_scores": {
    "rouge1": 0.68,
    "rouge2": 0.45,
    "rougeL": 0.62
  }
}
```

## 🌐 Web UI Features

Access: **http://localhost:8001**

### Tabs:
1. **📝 Single Document** - Paste or upload one document
2. **📦 Batch Upload** - Upload multiple files at once
3. **📚 History** - View saved summaries (localStorage)
4. **⚙️ Settings** - Configure preferences

### Features:
- ✅ Real-time progress tracking with spinners
- ✅ Document history (max 50 items, browser storage)
- ✅ Download results (TXT, JSON formats)
- ✅ Copy to clipboard functionality
- ✅ Language selector (15 languages)
- ✅ Intent selector (6 types)
- ✅ Quality preference selector (speed/balanced/quality)
- ✅ Persistent settings (saved in browser)
- ✅ Error alerts with auto-dismiss
- ✅ Responsive design (desktop & tablet friendly)

## 💻 Python Usage Examples

### Basic Single Document
```python
from src.summarizer import TechnicalDocumentSummarizer

summarizer = TechnicalDocumentSummarizer()
result = summarizer.auto_summarize(
    document="Your text here...",
    quality_preference="balanced"
)
print(result['summary'])
```

### Batch Processing
```python
documents = [
    "Document 1 text...",
    "Document 2 text...",
    "Document 3 text..."
]
results = summarizer.summarize_batch(documents)
for i, result in enumerate(results):
    print(f"Doc {i+1}: {result['summary']}")
```

### With Custom Intent
```python
result = summarizer.auto_summarize(
    document="Technical paper...",
    quality_preference="quality",  # Use best model + RAG
    language="spanish",
    intent="methodology"  # Focus on methods used
)
```

### Export Results
```python
from src.exporters import SummaryExporter

exporter = SummaryExporter()
exporter.export_json(result, "output.json")
exporter.export_pdf(result, "output.pdf")
exporter.export_markdown(result, "output.md")
```

## 🔧 Testing with Postman

1. **Start API Server:**
   ```bash
   python main.py
   # Select: 3
   ```

2. **Import Collection:**
   - Open Postman
   - Click Import → Select `Postman_Collection.json`

3. **Run Tests:**
   - 7 essential tests ready to run
   - Health check → Language test → Batch test → etc.
   - All tests include assertions and performance metrics

## 📊 Performance Metrics

| Mode | Model | Latency | Quality | Memory |
|------|-------|---------|---------|--------|
| Speed (⚡) | T5-Small | < 2 sec | 0.70 | 1.5 GB |
| Balanced (⚖️) | T5-Base | 2-5 sec | 0.85 | 3 GB |
| Quality (✨) | T5-Large + RAG | 5-10 sec | 0.95 | 6 GB |

## 🛠️ Configuration

Edit `config.json` to customize:
- Supported languages
- Summarization intent types
- Chunk size for RAG
- Model selection criteria
- Default quality preference
- Min/max summary lengths

## 📦 Core Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| **transformers** | Pre-trained models | Latest |
| **torch** | Deep learning framework | Latest |
| **fastapi** | REST API framework | Latest |
| **uvicorn** | ASGI server | Latest |
| **sentence-transformers** | Embeddings | Latest |
| **faiss-cpu** | Vector search | Latest |
| **rouge-score** | Quality metrics | Latest |
| **reportlab** | PDF generation | Latest |

See `requirements.txt` for complete list with versions.

## 🎓 How It Works

```
1. INPUT: Read document (text/file)
   ↓
2. PREPROCESSING: Clean, tokenize, chunk (512 tokens + overlap)
   ↓
3. ANALYSIS: Count words, measure complexity, detect language
   ↓
4. MODEL SELECTION:
   - Simple doc (< 500 words) → T5-Small (fast)
   - Medium doc (500-2000 words) → T5-Base (balanced)
   - Complex doc (2000-5000 words) → Pegasus + RAG (quality)
   - Very complex (> 5000 words) → T5-Large + RAG (best)
   ↓
5. RAG PIPELINE (optional, for complex docs):
   - Generate embeddings for each chunk
   - Build FAISS vector index
   - Retrieve most relevant chunks
   - Feed to summarization model
   ↓
6. SUMMARIZATION: Generate abstractive summary
   ↓
7. EVALUATION:
   - Calculate ROUGE scores
   - Confidence score (0-1)
   - Extract keywords
   ↓
8. OUTPUT: Export in desired format
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: rouge_score` | `pip install rouge_score` |
| Models not downloading | `python models/download_models.py` |
| Port 8000/8001 already in use | Change port in CLI prompt |
| CUDA/GPU not detected | Will auto-fallback to CPU |
| Slow performance | Use Speed mode or reduce document size |

## 📄 Project Status

✅ **Complete & Production-Ready**
- All 4 operation modes fully functional
- API endpoints tested & documented
- Web UI with all requested features
- Batch processing working
- Export formats (JSON, PDF, TXT, MD)
- Multi-language support (15 languages)
- Quality evaluation metrics
- Error handling & logging

## 📚 References

- **Transformers Library:** https://huggingface.co/docs/transformers
- **PyTorch Docs:** https://pytorch.org/docs
- **FastAPI:** https://fastapi.tiangolo.com
- **FAISS:** https://github.com/facebookresearch/faiss
- **Sentence-Transformers:** https://www.sbert.net/

### Research Papers
- "Attention is All You Need" (Vaswani et al., 2017)
- "BART: Denoising Sequence-to-Sequence Pretraining" (Lewis et al., 2019)
- "PEGASUS: Pre-training with Extracted Gap-sentences for Abstractive Summarization" (Zhang et al., 2019)
- "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (Raffel et al., 2019)
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)

## 👥 Contributing

Contributions welcome! Areas for improvement:
- [ ] Additional language models
- [ ] Fine-tuned models for specific domains
- [ ] More export formats (DOCX, HTML)
- [ ] User authentication for web UI
- [ ] Database integration for history
- [ ] Docker containerization
- [ ] Performance optimizations

## 📞 Support

For issues, questions, or suggestions:
1. Check [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)
2. Review existing GitHub issues
3. Create detailed bug reports

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated:** February 24, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
