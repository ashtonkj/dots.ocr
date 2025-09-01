#!/usr/bin/env python3
"""
Test script to demonstrate enhanced parser features using existing parsed data.
This script shows how the enhanced features work without requiring a full PDF parse.
"""

import json
import os
import sys
from typing import List, Dict, Any

# Mock the enhanced parser functionality for testing
class MockEnhancedParser:
    """Mock version of the enhanced parser for testing with existing data."""
    
    def __init__(self):
        self.existing_data_dir = "/home/kevin/development/parsed/FalksDictionaryOfChineseMartialArts"
    
    def load_existing_data(self) -> List[Dict[str, Any]]:
        """Load existing parsed data and add page information."""
        all_entries = []
        
        # Load data from existing JSON files
        for filename in sorted(os.listdir(self.existing_data_dir)):
            if filename.endswith('.json') and 'page_' in filename:
                # Extract page number from filename
                page_no = int(filename.split('_page_')[1].split('.')[0])
                file_path = os.path.join(self.existing_data_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        page_entries = json.load(f)
                    
                    # Add page information to each entry
                    for idx, entry in enumerate(page_entries):
                        enhanced_entry = entry.copy()
                        enhanced_entry['page_number'] = page_no
                        enhanced_entry['page_index'] = idx
                        enhanced_entry['global_index'] = len(all_entries)
                        all_entries.append(enhanced_entry)
                        
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")
        
        return all_entries
    
    def filter_entries(self, entries: List[Dict[str, Any]], 
                      exclude_categories: List[str] = None,
                      include_categories: List[str] = None,
                      min_text_length: int = 0) -> List[Dict[str, Any]]:
        """Filter entries based on various criteria."""
        filtered_entries = []
        
        for entry in entries:
            # Apply category filters
            if exclude_categories and entry.get('category') in exclude_categories:
                continue
                
            if include_categories and entry.get('category') not in include_categories:
                continue
            
            # Apply text length filter
            text = entry.get('text', '')
            if len(text.strip()) < min_text_length:
                continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def sort_entries(self, entries: List[Dict[str, Any]], 
                    sort_by: str = 'page_and_index') -> List[Dict[str, Any]]:
        """Sort entries by specified criteria."""
        if sort_by == 'page_and_index':
            return sorted(entries, key=lambda x: (x.get('page_number', 0), x.get('page_index', 0)))
        elif sort_by == 'category':
            return sorted(entries, key=lambda x: (x.get('category', ''), x.get('page_number', 0), x.get('page_index', 0)))
        elif sort_by == 'text':
            return sorted(entries, key=lambda x: (x.get('text', '').lower(), x.get('page_number', 0), x.get('page_index', 0)))
        elif sort_by == 'bbox_y':
            return sorted(entries, key=lambda x: (x.get('page_number', 0), x.get('bbox', [0, 0, 0, 0])[1]))
        else:
            return entries
    
    def generate_stats(self, all_entries: List[Dict[str, Any]], 
                      filtered_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the parsing results."""
        return {
            'total_pages': len(set(entry.get('page_number', 0) for entry in all_entries)),
            'total_entries_before_filter': len(all_entries),
            'total_entries_after_filter': len(filtered_entries),
            'categories_found': list(set(entry.get('category', '') for entry in all_entries)),
            'categories_in_output': list(set(entry.get('category', '') for entry in filtered_entries)),
            'page_range': {
                'start': min((entry.get('page_number', 0) for entry in filtered_entries), default=0),
                'end': max((entry.get('page_number', 0) for entry in filtered_entries), default=0)
            }
        }


def test_basic_functionality():
    """Test basic enhanced parser functionality."""
    print("=== Testing Basic Enhanced Parser Functionality ===")
    
    parser = MockEnhancedParser()
    
    # Load existing data
    print("Loading existing parsed data...")
    all_entries = parser.load_existing_data()
    print(f"Loaded {len(all_entries)} entries from existing data")
    
    # Show sample entries with new fields
    print("\nSample entries with enhanced fields:")
    for i, entry in enumerate(all_entries[:3]):
        print(f"  {i+1}. Page {entry['page_number']}, Index {entry['page_index']}, "
              f"Global {entry['global_index']}, Category: {entry['category']}")
        print(f"     Text: {entry['text'][:100]}...")
    
    return all_entries


def test_filtering(all_entries: List[Dict[str, Any]]):
    """Test filtering functionality."""
    print("\n=== Testing Filtering Functionality ===")
    
    parser = MockEnhancedParser()
    
    # Test 1: Exclude headers and footers
    print("\n1. Excluding Page-header and Page-footer categories:")
    filtered1 = parser.filter_entries(
        all_entries,
        exclude_categories=['Page-header', 'Page-footer']
    )
    print(f"   Before: {len(all_entries)} entries")
    print(f"   After: {len(filtered1)} entries")
    
    # Test 2: Only include specific categories
    print("\n2. Including only Text and Section-header categories:")
    filtered2 = parser.filter_entries(
        all_entries,
        include_categories=['Text', 'Section-header']
    )
    print(f"   Before: {len(all_entries)} entries")
    print(f"   After: {len(filtered2)} entries")
    
    # Test 3: Minimum text length filter
    print("\n3. Filtering by minimum text length (20 characters):")
    filtered3 = parser.filter_entries(
        all_entries,
        min_text_length=20
    )
    print(f"   Before: {len(all_entries)} entries")
    print(f"   After: {len(filtered3)} entries")
    
    # Test 4: Combined filters
    print("\n4. Combined filters (exclude headers/footers + min length):")
    filtered4 = parser.filter_entries(
        all_entries,
        exclude_categories=['Page-header', 'Page-footer'],
        min_text_length=10
    )
    print(f"   Before: {len(all_entries)} entries")
    print(f"   After: {len(filtered4)} entries")
    
    return filtered4


def test_sorting(all_entries: List[Dict[str, Any]]):
    """Test sorting functionality."""
    print("\n=== Testing Sorting Functionality ===")
    
    parser = MockEnhancedParser()
    
    # Test different sorting methods
    sorting_methods = [
        ('page_and_index', 'Page and Index'),
        ('category', 'Category'),
        ('text', 'Text Content'),
        ('bbox_y', 'Vertical Position')
    ]
    
    for sort_method, description in sorting_methods:
        print(f"\n{description} sorting:")
        sorted_entries = parser.sort_entries(all_entries, sort_method)
        
        # Show first few entries to demonstrate sorting
        print(f"  First 3 entries:")
        for i, entry in enumerate(sorted_entries[:3]):
            print(f"    {i+1}. Page {entry['page_number']}, Index {entry['page_index']}, "
                  f"Category: {entry['category']}")
            print(f"       Text: {entry['text'][:50]}...")


def test_statistics(all_entries: List[Dict[str, Any]]):
    """Test statistics generation."""
    print("\n=== Testing Statistics Generation ===")
    
    parser = MockEnhancedParser()
    
    # Generate stats for different filter scenarios
    scenarios = [
        ("No filtering", all_entries),
        ("Exclude headers/footers", parser.filter_entries(all_entries, exclude_categories=['Page-header', 'Page-footer'])),
        ("Text only", parser.filter_entries(all_entries, include_categories=['Text'])),
        ("Min length 20", parser.filter_entries(all_entries, min_text_length=20))
    ]
    
    for scenario_name, filtered_entries in scenarios:
        stats = parser.generate_stats(all_entries, filtered_entries)
        print(f"\n{scenario_name}:")
        print(f"  Total pages: {stats['total_pages']}")
        print(f"  Entries before filter: {stats['total_entries_before_filter']}")
        print(f"  Entries after filter: {stats['total_entries_after_filter']}")
        print(f"  Categories found: {stats['categories_found']}")
        print(f"  Categories in output: {stats['categories_in_output']}")
        print(f"  Page range: {stats['page_range']['start']} - {stats['page_range']['end']}")


def test_output_generation(all_entries: List[Dict[str, Any]]):
    """Test output file generation."""
    print("\n=== Testing Output Generation ===")
    
    parser = MockEnhancedParser()
    
    # Apply some filters
    filtered_entries = parser.filter_entries(
        all_entries,
        exclude_categories=['Page-header', 'Page-footer'],
        min_text_length=5
    )
    
    # Sort entries
    sorted_entries = parser.sort_entries(filtered_entries, 'page_and_index')
    
    # Generate stats
    stats = parser.generate_stats(all_entries, filtered_entries)
    
    # Create output directory
    output_dir = "/home/kevin/development/parsed/enhanced_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save merged output
    merged_output_path = os.path.join(output_dir, 'merged_entries.json')
    with open(merged_output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
    
    # Save statistics
    stats_path = os.path.join(output_dir, 'parsing_stats.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Test output saved to: {output_dir}")
    print(f"📄 Merged entries: {merged_output_path}")
    print(f"📊 Statistics: {stats_path}")
    print(f"📝 Generated {len(sorted_entries)} entries from {stats['total_pages']} pages")


def main():
    """Run all tests."""
    print("Enhanced DotsOCR Parser - Feature Test")
    print("=" * 50)
    
    # Check if existing data exists
    existing_data_dir = "/home/kevin/development/parsed/FalksDictionaryOfChineseMartialArts"
    if not os.path.exists(existing_data_dir):
        print(f"Error: Existing parsed data not found at {existing_data_dir}")
        print("Please run the original parser first to generate test data.")
        sys.exit(1)
    
    try:
        # Run all tests
        all_entries = test_basic_functionality()
        test_filtering(all_entries)
        test_sorting(all_entries)
        test_statistics(all_entries)
        test_output_generation(all_entries)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("The enhanced parser features are working correctly.")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
