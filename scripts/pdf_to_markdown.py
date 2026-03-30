#!/usr/bin/env python3
"""
PDF to Markdown converter for GAP literature collection.
Extracts text from PDF files and converts to Markdown format.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_title_from_pdf(pdf_path):
    """Extract title from PDF metadata or first page."""
    try:
        doc = fitz.open(pdf_path)
        
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            doc.close()
            return metadata['title']
        
        # Try to extract from first page
        if len(doc) > 0:
            first_page = doc[0]
            text = first_page.get_text()
            lines = text.split('\n')
            # The title is usually the first non-empty line
            for line in lines[:10]:
                line = line.strip()
                if len(line) > 10 and len(line) < 200:
                    doc.close()
                    return line
        
        doc.close()
    except Exception as e:
        logger.warning(f"Could not extract title from {pdf_path}: {e}")
    
    return Path(pdf_path).stem.replace('_', ' ')

def pdf_to_markdown(pdf_path, output_path=None):
    """
    Convert PDF to Markdown format.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output Markdown file (optional)
    
    Returns:
        Path to output Markdown file
    """
    pdf_path = Path(pdf_path)
    
    if output_path is None:
        output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_path)
    
    logger.info(f"Converting {pdf_path.name} to Markdown...")
    
    try:
        doc = fitz.open(str(pdf_path))
        
        markdown_content = []
        
        # Extract metadata
        metadata = doc.metadata
        if metadata.get('title'):
            markdown_content.append(f"# {metadata['title']}\n")
        if metadata.get('author'):
            markdown_content.append(f"**Author**: {metadata['author']}\n")
        if metadata.get('subject'):
            markdown_content.append(f"**Subject**: {metadata['subject']}\n")
        if metadata.get('creator'):
            markdown_content.append(f"**Creator**: {metadata['creator']}\n")
        
        markdown_content.append(f"\n---\n\n")
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                # Add page separator for long documents
                if page_num > 0 and len(doc) > 5:
                    markdown_content.append(f"\n!!! page {page_num + 1} \"{pdf_path.stem}\"\n\n")
                
                # Clean up text
                text = clean_text(text)
                markdown_content.append(text)
                markdown_content.append("\n\n")
        
        doc.close()
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(markdown_content)
        
        logger.info(f"Successfully converted {pdf_path.name} to {output_path.name}")
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to convert {pdf_path.name}: {e}")
        return None

def clean_text(text):
    """Clean extracted text for better Markdown formatting."""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove excessive whitespace
        line = line.strip()
        if line:
            cleaned_lines.append(line)
    
    # Join with proper spacing
    text = '\n\n'.join(cleaned_lines)
    
    # Fix common PDF extraction issues
    text = text.replace('-\n', '')  # Remove hyphenation at line breaks
    
    return text

def process_directory(pdf_dir, output_dir=None):
    """
    Process all PDFs in a directory.
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory for output Markdown files (optional)
    
    Returns:
        List of successfully converted files
    """
    pdf_dir = Path(pdf_dir)
    
    if output_dir is None:
        output_dir = pdf_dir
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_dir}")
        return []
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    results = []
    for pdf_file in pdf_files:
        output_path = output_dir / pdf_file.with_suffix('.md').name
        result = pdf_to_markdown(pdf_file, output_path)
        if result:
            results.append(result)
    
    logger.info(f"Successfully converted {len(results)}/{len(pdf_files)} files")
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF files to Markdown')
    parser.add_argument('input', help='Input PDF file or directory containing PDFs')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-d', '--directory', action='store_true', help='Input is a directory')
    
    args = parser.parse_args()
    
    if args.directory or Path(args.input).is_dir():
        process_directory(args.input, args.output)
    else:
        result = pdf_to_markdown(args.input, args.output)
        if result:
            print(f"Converted to: {result}")
        sys.exit(0 if result else 1)
