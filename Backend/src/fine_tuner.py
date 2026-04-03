"""
Fine-tuning module for domain-specific models
"""

import logging
from typing import List, Dict, Optional
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments
import json

logger = logging.getLogger(__name__)


class SummarizationDataset(Dataset):
    """Dataset for summarization fine-tuning."""
    
    def __init__(self, documents: List[str], summaries: List[str], tokenizer, max_len: int = 512):
        """
        Initialize dataset.
        
        Args:
            documents: List of documents
            summaries: List of corresponding summaries
            tokenizer: HuggingFace tokenizer
            max_len: Maximum token length
        """
        self.documents = documents
        self.summaries = summaries
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.documents)
    
    def __getitem__(self, idx):
        document = str(self.documents[idx])
        summary = str(self.summaries[idx])
        
        # Tokenize input
        inputs = self.tokenizer(
            document,
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Tokenize target
        targets = self.tokenizer(
            summary,
            max_length=256,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': targets['input_ids'].squeeze(),
        }


class FineTuner:
    """Fine-tune summarization model on custom data."""
    
    def __init__(self, model, tokenizer, device: str = 'cuda'):
        """
        Initialize fine-tuner.
        
        Args:
            model: Pre-trained model
            tokenizer: Tokenizer
            device: Device to use
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
    
    def prepare_data(
        self,
        data_file: str
    ) -> tuple:
        """
        Prepare data from JSON file.
        
        Format: [{"document": "...", "summary": "..."}, ...]
        
        Args:
            data_file: Path to JSON file
            
        Returns:
            Tuple of (documents, summaries)
        """
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = [item['document'] for item in data]
        summaries = [item['summary'] for item in data]
        
        logger.info(f"Loaded {len(documents)} training examples")
        return documents, summaries
    
    def fine_tune(
        self,
        documents: List[str],
        summaries: List[str],
        output_dir: str = 'models/fine_tuned',
        num_epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 2e-5
    ) -> str:
        """
        Fine-tune model on custom data.
        
        Args:
            documents: Training documents
            summaries: Training summaries
            output_dir: Output directory
            num_epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            
        Returns:
            Path to fine-tuned model
        """
        # Create dataset
        train_dataset = SummarizationDataset(
            documents, 
            summaries, 
            self.tokenizer
        )
        
        # Training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            save_steps=len(train_dataset) // batch_size,
            save_total_limit=2,
            logging_steps=10,
        )
        
        # Trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=self.tokenizer,
        )
        
        # Train
        logger.info("Starting fine-tuning...")
        trainer.train()
        
        # Save
        trainer.save_model(output_dir)
        logger.info(f"Fine-tuned model saved to {output_dir}")
        
        return output_dir
    
    def quick_fine_tune(
        self,
        data_file: str,
        output_dir: str = 'models/fine_tuned'
    ) -> str:
        """
        Quick fine-tuning from JSON file.
        
        Args:
            data_file: Path to training data JSON
            output_dir: Output directory
            
        Returns:
            Path to fine-tuned model
        """
        documents, summaries = self.prepare_data(data_file)
        
        return self.fine_tune(
            documents,
            summaries,
            output_dir=output_dir,
            num_epochs=2,
            batch_size=4
        )
