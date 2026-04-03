# Data Directory

This directory contains datasets and data processing utilities for the Intent-Aware Context-Preserving Summarization project.

## Directory Structure

```
data/
├── README.md                 # This file
├── sample_documents.json     # Sample technical documents for testing
├── download_datasets.py      # Script to download public datasets
├── dataset_info.json         # Dataset metadata and configurations
├── processing/               # Data processing scripts
│   ├── arxiv_loader.py
│   ├── pubmed_loader.py
│   └── document_processor.py
└── raw/                      # Raw downloaded datasets
```

## Available Datasets

### 1. arXiv Dataset
- **Source**: https://www.kaggle.com/datasets/Cornell-University/arxiv
- **Documents**: 1.7M+ research papers
- **Domains**: Physics, Computer Science, Mathematics, etc.
- **Size**: ~90GB (full), 5GB+ (samples)

### 2. PubMed Dataset
- **Source**: https://pubmed.ncbi.nlm.nih.gov/
- **Documents**: 30M+ biomedical articles
- **Domain**: Medical, biomedical literature
- **API**: Free API available

### 3. Scientific Papers (S2ORC)
- **Source**: https://www.semanticscholar.org/
- **Documents**: 200M+ scientific papers
- **Coverage**: All domains

## Getting Data

### Option 1: Use Sample Data
Pre-loaded sample documents are available in `sample_documents.json`:
```python
import json

with open('data/sample_documents.json', 'r') as f:
    sample_data = json.load(f)
    
for doc in sample_data['documents']:
    print(doc['title'])
    print(doc['abstract'])
```

### Option 2: Download Kaggle arXiv Dataset
```bash
# Install kaggle CLI
pip install kaggle

# Configure credentials (~/.kaggle/kaggle.json)
# Download dataset
kaggle datasets download -d Cornell-University/arxiv

# Extract
unzip arxiv.zip -d data/raw/
```

### Option 3: Download via Script
```bash
python data/download_datasets.py --arxiv-sample
python data/download_datasets.py --pubmed-sample
```

### Option 4: Use Hugging Face Datasets
```python
from datasets import load_dataset

# arXiv dataset
arxiv = load_dataset('arxiv_dataset')

# Scientific papers
papers = load_dataset('scientific_papers', 'arxiv')
```

## Data Format

### Document Structure
```json
{
  "id": "2301.00123",
  "title": "Attention Is All You Need",
  "abstract": "The dominant sequence transduction...",
  "authors": ["Ashish Vaswani", "..."],
  "published_date": "2023-01-01",
  "categories": ["cs.LG", "cs.AI"],
  "full_text": "Introduction...",
  "sections": {
    "introduction": "...",
    "methodology": "...",
    "results": "...",
    "conclusion": "..."
  }
}
```

## Loading Data

### Using Custom Loader
```python
from data.processing.document_processor import DocumentProcessor

processor = DocumentProcessor()
documents = processor.load_documents('data/raw/arxiv_sample.jsonl')
```

### Using Hugging Face
```python
from datasets import load_dataset

# Load paper summaries
dataset = load_dataset('scientific_papers', 'arxiv')
print(dataset['train'][0])
```

## Data Processing

### Preprocess Documents
```python
from data.processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Load and process
docs = processor.load_documents('data/raw/documents.jsonl')
processed = processor.process_batch(docs)

# Save processed data
processor.save_processed('data/processed/documents.json')
```

### Create Intent-Labeled Dataset
```python
from data.processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Create labeled dataset for intent classification
labeled_data = processor.create_intent_labels(
    documents=docs,
    intents=['methodology', 'results', 'conclusion']
)

processor.save_labeled('data/labeled/intent_labeled.jsonl')
```

## Data Statistics

| Dataset | Documents | Avg Length | Size |
|---------|-----------|-----------|------|
| arXiv Sample | 1,000 | 8KB | 8MB |
| PubMed Sample | 5,000 | 5KB | 25MB |
| Full arXiv | 1.7M | 8KB | 13GB+ |
| Full PubMed | 30M | 5KB | 150GB+ |

## Storage Recommendations

- **Sample Data**: 100MB (testing/development)
- **Small Dataset**: 1-5GB (local training)
- **Full Datasets**: 100GB+ (cloud storage recommended)

## Data Privacy

- All datasets are from public sources
- Respect dataset licenses and terms
- Follow GDPR and data privacy regulations
- Anonymize personal information if needed

## References

- arXiv: https://arxiv.org
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- Semantic Scholar: https://www.semanticscholar.org/
- Hugging Face Datasets: https://huggingface.co/datasets

---

**Last Updated**: January 15, 2024
