# Models Directory

This directory contains pre-trained and fine-tuned models for the Intent-Aware Context-Preserving Summarization project.

## Directory Structure

```
models/
├── README.md                 # This file
├── download_models.py        # Script to download pre-trained models
├── model_configs.json        # Model configurations and metadata
├── checkpoints/              # Fine-tuned model checkpoints
└── tokenizers/               # Tokenizer files
```

## Available Models

### Pre-trained Models from Hugging Face

| Model Name | Model ID | Size | Best For |
|-----------|----------|------|----------|
| T5-Small | google-t5/t5-small | ~77MB | Quick testing, prototyping |
| T5-Base | google-t5/t5-base | ~220MB | General use, production |
| T5-Large | google-t5/t5-large | ~738MB | High-quality summaries |
| BART-Base | facebook/bart-base | ~558MB | General summarization |
| BART-Large-CNN | facebook/bart-large-cnn | ~1.6GB | News/article summarization |
| PEGASUS-arXiv | google/pegasus-arxiv | ~568MB | Scientific papers |
| PEGASUS-PubMed | google/pegasus-pubmed | ~562MB | Medical/biomedical documents |
| LED-Base | allenai/led-base-16384 | ~660MB | Long documents (4096 tokens) |

## Downloading Models

### Automatic Download
```bash
python models/download_models.py
```

### Manual Download
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Download T5-base
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google-t5/t5-base")

# Save locally
tokenizer.save_pretrained("models/t5-base-tokenizer")
model.save_pretrained("models/t5-base-model")
```

## Fine-tuned Models

Fine-tuned models will be stored in `models/checkpoints/` after training:
- `intent-classifier-v1/` - Intent detection model
- `summarizer-technical-v1/` - Fine-tuned summarization model
- `summarizer-intent-aware-v1/` - Intent-aware summarization model

## Model Configuration

Edit `model_configs.json` to configure:
- Model selection
- Tokenization parameters
- Generation settings
- Evaluation metrics

## Using Models

### Load Pre-trained Model
```python
from src.models import SummarizationModelLoader

loader = SummarizationModelLoader(model_name='t5-base')
model, tokenizer = loader.load_model()
```

### Load Fine-tuned Checkpoint
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "models/checkpoints/summarizer-technical-v1"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
```

## Storage Requirements

- **Small Models**: ~500MB total
- **Large Models**: ~3GB total
- **With Fine-tuning Data**: ~5-10GB

## GPU Memory Requirements

| Model | GPU Memory |
|-------|-----------|
| T5-Small | 2GB |
| T5-Base | 6GB |
| T5-Large | 12GB+ |
| BART-Base | 6GB |
| BART-Large-CNN | 12GB+ |
| LED-Base | 8GB |

## Best Practices

1. **Start with small models** for testing and development
2. **Use cached models** to avoid repeated downloads
3. **Monitor GPU memory** when loading large models
4. **Save fine-tuned models** with meaningful version numbers
5. **Document model changes** in model metadata

## Troubleshooting

### Out of Memory Error
```python
import torch
torch.cuda.empty_cache()  # Clear GPU cache
# Or use CPU: device='cpu'
```

### Model Download Issues
- Check internet connection
- Verify Hugging Face API is accessible
- Try downloading specific model versions
- Use `cache_dir` parameter to specify custom location

### Tokenizer Mismatch
Ensure tokenizer version matches model version:
```python
tokenizer = AutoTokenizer.from_pretrained(model_path)  # Load matching tokenizer
```

## References

- Hugging Face Models: https://huggingface.co/models
- Transformers Documentation: https://huggingface.co/docs/transformers
- Model Cards: https://huggingface.co/docs/hub/models-cards

## Contributing

If you fine-tune new models:
1. Save with meaningful names and versions
2. Document performance metrics
3. Include training parameters
4. Add model cards with descriptions
5. Update this README

---

**Last Updated**: January 15, 2024
