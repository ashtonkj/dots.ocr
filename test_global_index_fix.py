#!/usr/bin/env python3
"""
Test script to verify the global_index calculation fix.
"""

import json
import os
import sys
sys.path.append('.')

from parse_pdf_enhanced import EnhancedDotsOCRParser


def test_global_index_calculation():
    """Test that global_index is calculated correctly."""
    print("Testing global_index calculation...")
    
    # Create a mock parser instance
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150
    )
    
    # Mock page results that simulate the actual parser output
    mock_page_results = [
        {
            'page_no': 0,
            'layout_info_path': '/home/kevin/development/parsed/FalksDictionaryOfChineseMartialArts/FalksDictionaryOfChineseMartialArts_page_0.json'
        },
        {
            'page_no': 1,
            'layout_info_path': '/home/kevin/development/parsed/FalksDictionaryOfChineseMartialArts/FalksDictionaryOfChineseMartialArts_page_1.json'
        }
    ]
    
    # Test the add_page_info method
    enhanced_entries = enhanced_parser.add_page_info(mock_page_results)
    
    print(f"Total entries processed: {len(enhanced_entries)}")
    
    # Check the first few entries to verify global_index calculation
    print("\nFirst 10 entries with their indices:")
    for i, entry in enumerate(enhanced_entries[:10]):
        print(f"  Entry {i}: Page {entry['page_number']}, Index {entry['page_index']}, Global {entry['global_index']}")
        
        # Verify that global_index matches the expected value
        expected_global = i
        if entry['global_index'] != expected_global:
            print(f"    ❌ ERROR: Expected global_index {expected_global}, got {entry['global_index']}")
        else:
            print(f"    ✅ Correct")
    
    # Check that global_index is sequential across pages
    print("\nVerifying global_index is sequential across pages:")
    prev_global = -1
    for entry in enhanced_entries:
        if entry['global_index'] != prev_global + 1:
            print(f"  ❌ ERROR: Non-sequential global_index detected!")
            print(f"     Previous: {prev_global}, Current: {entry['global_index']}")
            print(f"     Entry: Page {entry['page_number']}, Index {entry['page_index']}")
            return False
        prev_global = entry['global_index']
    
    print("  ✅ All global_index values are sequential")
    
    # Check that page 0 entries have global_index equal to page_index
    print("\nVerifying page 0 entries have global_index = page_index:")
    for entry in enhanced_entries:
        if entry['page_number'] == 0:
            if entry['global_index'] != entry['page_index']:
                print(f"  ❌ ERROR: Page 0 entry has global_index {entry['global_index']} != page_index {entry['page_index']}")
                return False
    
    print("  ✅ All page 0 entries have correct global_index")
    
    return True


def main():
    """Run the global_index test."""
    print("Global Index Calculation Test")
    print("=" * 40)
    
    # Check if the test data exists
    test_file = "/home/kevin/development/parsed/FalksDictionaryOfChineseMartialArts/FalksDictionaryOfChineseMartialArts_page_0.json"
    if not os.path.exists(test_file):
        print(f"Error: Test data not found at {test_file}")
        print("Please run the original parser first to generate test data.")
        sys.exit(1)
    
    try:
        success = test_global_index_calculation()
        
        if success:
            print("\n" + "=" * 40)
            print("✅ Global index calculation test passed!")
            print("The fix is working correctly.")
        else:
            print("\n" + "=" * 40)
            print("❌ Global index calculation test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
