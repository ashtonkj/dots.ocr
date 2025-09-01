#!/usr/bin/env python3
"""
Example usage of the Enhanced DotsOCR Parser

This script demonstrates various ways to use the enhanced parser with
filtering, indexing, and merging capabilities.
"""

import sys
import os
sys.path.append('.')

from parse_pdf_enhanced import EnhancedDotsOCRParser


def example_basic_usage():
    """Basic usage example with default settings."""
    print("=== Basic Usage Example ===")
    
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150,
        max_completion_tokens=65536
    )
    
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path="/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf",
        output_dir="/home/kevin/development/parsed/enhanced_basic",
        start_page=20,
        end_page=21
    )
    
    print(f"Processed {result['stats']['total_pages']} pages")
    print(f"Found {result['stats']['total_entries_before_filter']} total entries")
    print(f"Output {result['stats']['total_entries_after_filter']} filtered entries")
    print(f"Categories found: {result['stats']['categories_found']}")
    print(f"Categories in output: {result['stats']['categories_in_output']}")


def example_with_filtering():
    """Example with filtering to exclude headers and footers."""
    print("\n=== Filtering Example ===")
    
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150,
        max_completion_tokens=65536
    )
    
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path="/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf",
        output_dir="/home/kevin/development/parsed/enhanced_filtered",
        start_page=20,
        end_page=21,
        exclude_categories=['Page-header', 'Page-footer'],
        min_text_length=5  # Only keep entries with at least 5 characters
    )
    
    print(f"After filtering: {result['stats']['total_entries_after_filter']} entries")
    print(f"Categories in output: {result['stats']['categories_in_output']}")


def example_with_custom_filter():
    """Example with a custom filter function."""
    print("\n=== Custom Filter Example ===")
    
    def custom_filter(entry):
        """Custom filter: only keep text entries that contain Chinese characters."""
        import re
        
        # Check if it's a text entry
        if entry.get('category') != 'Text':
            return False
        
        # Check if it contains Chinese characters
        text = entry.get('text', '')
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(chinese_pattern.search(text))
    
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150,
        max_completion_tokens=65536
    )
    
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path="/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf",
        output_dir="/home/kevin/development/parsed/enhanced_custom_filter",
        start_page=20,
        end_page=21,
        custom_filter=custom_filter
    )
    
    print(f"After custom filtering: {result['stats']['total_entries_after_filter']} entries")
    
    # Show some examples of the filtered entries
    print("\nSample filtered entries:")
    for i, entry in enumerate(result['entries'][:3]):
        print(f"  {i+1}. Page {entry['page_number']}, Index {entry['page_index']}: {entry['text'][:100]}...")


def example_with_sorting():
    """Example with different sorting options."""
    print("\n=== Sorting Example ===")
    
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150,
        max_completion_tokens=65536
    )
    
    # Sort by category
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path="/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf",
        output_dir="/home/kevin/development/parsed/enhanced_sorted_by_category",
        start_page=20,
        end_page=21,
        sort_by='category'
    )
    
    print(f"Sorted by category: {result['stats']['total_entries_after_filter']} entries")
    
    # Show the first few entries to demonstrate sorting
    print("\nFirst few entries (sorted by category):")
    current_category = None
    for entry in result['entries'][:10]:
        if entry['category'] != current_category:
            current_category = entry['category']
            print(f"\n  Category: {current_category}")
        print(f"    Page {entry['page_number']}, Index {entry['page_index']}: {entry['text'][:50]}...")


def example_include_only_specific_categories():
    """Example that only includes specific categories."""
    print("\n=== Include Only Specific Categories Example ===")
    
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150,
        max_completion_tokens=65536
    )
    
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path="/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf",
        output_dir="/home/kevin/development/parsed/enhanced_text_only",
        start_page=20,
        end_page=21,
        include_categories=['Text', 'Section-header']  # Only keep text and section headers
    )
    
    print(f"Only Text and Section-header categories: {result['stats']['total_entries_after_filter']} entries")
    print(f"Categories in output: {result['stats']['categories_in_output']}")


if __name__ == "__main__":
    print("Enhanced DotsOCR Parser Examples")
    print("=" * 50)
    
    # Check if the PDF file exists
    pdf_path = "/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        print("Please update the pdf_path variable in this script to point to your PDF file.")
        sys.exit(1)
    
    try:
        # Run examples
        example_basic_usage()
        example_with_filtering()
        example_with_custom_filter()
        example_with_sorting()
        example_include_only_specific_categories()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the output directories for the results.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)
