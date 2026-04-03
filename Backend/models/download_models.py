"""
Script to download pre-trained models from Hugging Face
"""

import os
import argparse
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm


# Available models
AVAILABLE_MODELS = {
    't5-small': 'google-t5/t5-small',
    't5-base': 'google-t5/t5-base',
    't5-large': 'google-t5/t5-large',
    'bart-base': 'facebook/bart-base',
    'bart-large-cnn': 'facebook/bart-large-cnn',
    'pegasus-arxiv': 'google/pegasus-arxiv',
    'pegasus-pubmed': 'google/pegasus-pubmed',
    'led-base': 'allenai/led-base-16384',
}


def download_model(model_name, model_id, save_dir='models'):
    """
    Download a model and tokenizer from Hugging Face.
    
    Args:
        model_name: Short name for the model
        model_id: Hugging Face model ID
        save_dir: Directory to save models
    """
    print(f"\nDownloading {model_name}...")
    print(f"Model ID: {model_id}")
    
    # Create directory structure
    model_path = os.path.join(save_dir, model_name)
    tokenizer_path = os.path.join(save_dir, f"{model_name}-tokenizer")
    
    Path(model_path).mkdir(parents=True, exist_ok=True)
    Path(tokenizer_path).mkdir(parents=True, exist_ok=True)
    
    try:
        # Download tokenizer
        print(f"Downloading tokenizer to {tokenizer_path}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.save_pretrained(tokenizer_path)
        print(f"✓ Tokenizer saved")
        
        # Download model
        print(f"Downloading model to {model_path}...")
        print("This may take a few minutes depending on model size...")
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        model.save_pretrained(model_path)
        print(f"✓ Model saved")
        
        print(f"✓ Successfully downloaded {model_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error downloading {model_name}: {str(e)}")
        return False


def list_available_models():
    """List all available models."""
    print("\nAvailable Models:")
    print("=" * 60)
    for name, model_id in AVAILABLE_MODELS.items():
        print(f"{name:20} -> {model_id}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Download pre-trained models from Hugging Face'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Specific model to download (use --list to see options)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all available models'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available models'
    )
    parser.add_argument(
        '--save-dir',
        type=str,
        default='models',
        help='Directory to save models (default: models)'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_models()
        return
    
    if args.all:
        print("Downloading all available models...")
        successful = 0
        failed = 0
        
        for model_name, model_id in AVAILABLE_MODELS.items():
            if download_model(model_name, model_id, args.save_dir):
                successful += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Download Summary: {successful} successful, {failed} failed")
        print("=" * 60)
        
    elif args.model:
        if args.model in AVAILABLE_MODELS:
            model_id = AVAILABLE_MODELS[args.model]
            download_model(args.model, model_id, args.save_dir)
        else:
            print(f"Model '{args.model}' not found")
            print("Available models:")
            list_available_models()
    else:
        # Default: download small model for quick start
        print("No model specified. Downloading t5-small for quick start...")
        download_model('t5-small', AVAILABLE_MODELS['t5-small'], args.save_dir)
        print("\nUse --all to download all models or --model <name> for specific models")
        print("Use --list to see all available models")


if __name__ == '__main__':
    main()
