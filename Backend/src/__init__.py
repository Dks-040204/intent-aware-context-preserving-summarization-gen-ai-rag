"""
Intent-Aware Context-Preserving Summarization of Long Technical Documents
Main package initialization
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from . import preprocessing
from . import models
from . import summarizer
from . import utils

__all__ = ['preprocessing', 'models', 'summarizer', 'utils']
