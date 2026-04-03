"""
Export summaries to different formats (PDF, Word, JSON, Text)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SummaryExporter:
    """Export summaries to multiple formats."""
    
    def __init__(self, output_dir: str = 'results'):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_json(
        self, 
        summary: str,
        metadata: Dict[str, Any] = None,
        filename: str = None
    ) -> str:
        """
        Export summary as JSON with metadata.
        
        Args:
            summary: Summary text
            metadata: Additional metadata
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to output file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'summary_{timestamp}.json'
        
        filepath = self.output_dir / filename
        
        data = {
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary exported to JSON: {filepath}")
        return str(filepath)
    
    def export_text(
        self,
        summary: str,
        filename: str = None
    ) -> str:
        """
        Export summary as plain text.
        
        Args:
            summary: Summary text
            filename: Output filename
            
        Returns:
            Path to output file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'summary_{timestamp}.txt'
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Summary exported to TXT: {filepath}")
        return str(filepath)
    
    def export_pdf(
        self,
        summary: str,
        title: str = "Summary",
        filename: str = None
    ) -> str:
        """
        Export summary as PDF (lightweight reportlab).
        
        Args:
            summary: Summary text
            title: PDF title
            filename: Output filename
            
        Returns:
            Path to output file
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'summary_{timestamp}.pdf'
            
            filepath = self.output_dir / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Add title
            story.append(Paragraph(title, styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Add summary
            story.append(Paragraph(summary, styles['BodyText']))
            
            doc.build(story)
            logger.info(f"Summary exported to PDF: {filepath}")
            return str(filepath)
        
        except ImportError:
            logger.warning("reportlab not installed. Exporting as text instead.")
            return self.export_text(summary, filename)
    
    def export_markdown(
        self,
        summary: str,
        title: str = "Summary",
        metadata: Dict[str, Any] = None,
        filename: str = None
    ) -> str:
        """
        Export summary as Markdown.
        
        Args:
            summary: Summary text
            title: Document title
            metadata: Additional metadata
            filename: Output filename
            
        Returns:
            Path to output file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'summary_{timestamp}.md'
        
        filepath = self.output_dir / filename
        
        content = f"# {title}\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if metadata:
            content += "## Metadata\n\n"
            for key, value in metadata.items():
                content += f"- **{key}:** {value}\n"
            content += "\n"
        
        content += "## Summary\n\n"
        content += summary
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Summary exported to Markdown: {filepath}")
        return str(filepath)
    
    def export_batch(
        self,
        summaries: Dict[str, str],
        format: str = 'json',
        filename: str = None
    ) -> str:
        """
        Export multiple summaries at once.
        
        Args:
            summaries: Dictionary of {name: summary}
            format: Export format ('json', 'txt', 'md')
            filename: Output filename
            
        Returns:
            Path to output file
        """
        if format == 'json':
            data = {
                'timestamp': datetime.now().isoformat(),
                'summaries': summaries
            }
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'batch_summaries_{timestamp}.json'
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == 'txt':
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'batch_summaries_{timestamp}.txt'
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                for name, summary in summaries.items():
                    f.write(f"=== {name} ===\n")
                    f.write(summary)
                    f.write("\n\n")
        
        logger.info(f"Batch summaries exported: {filepath}")
        return str(filepath)
