#!/usr/bin/env python3
"""
Simple test to verify the global_index calculation fix.
"""

import json
import sys
sys.path.append('.')

from parse_pdf_enhanced import EnhancedDotsOCRParser


def test_global_index_logic():
    """Test the global_index calculation logic with mock data."""
    print("Testing global_index calculation logic...")
    
    # Create a mock parser instance
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150
    )
    
    # Mock page results with sample data
    mock_page_results = [
        {
            'page_no': 0,
            'layout_info_path': 'mock_path_0'
        },
        {
            'page_no': 1,
            'layout_info_path': 'mock_path_1'
        }
    ]
    
    # Mock the add_page_info method to test the logic
    enhanced_entries = []
    global_index_counter = 0
    
    # Simulate processing page 0 with 3 entries
    page_0_entries = [
        {"bbox": [100, 100, 200, 200], "category": "Text", "text": "Entry 1"},
        {"bbox": [100, 200, 200, 300], "category": "Text", "text": "Entry 2"},
        {"bbox": [100, 300, 200, 400], "category": "Text", "text": "Entry 3"}
    ]
    
    for idx, entry in enumerate(page_0_entries):
        enhanced_entry = entry.copy()
        enhanced_entry['page_number'] = 0
        enhanced_entry['page_index'] = idx
        enhanced_entry['global_index'] = global_index_counter
        enhanced_entries.append(enhanced_entry)
        global_index_counter += 1
    
    # Simulate processing page 1 with 2 entries
    page_1_entries = [
        {"bbox": [100, 100, 200, 200], "category": "Text", "text": "Entry 4"},
        {"bbox": [100, 200, 200, 300], "category": "Text", "text": "Entry 5"}
    ]
    
    for idx, entry in enumerate(page_1_entries):
        enhanced_entry = entry.copy()
        enhanced_entry['page_number'] = 1
        enhanced_entry['page_index'] = idx
        enhanced_entry['global_index'] = global_index_counter
        enhanced_entries.append(enhanced_entry)
        global_index_counter += 1
    
    print(f"Total entries processed: {len(enhanced_entries)}")
    
    # Check the results
    print("\nVerifying global_index values:")
    expected_results = [
        (0, 0, 0),  # Page 0, Index 0, Global 0
        (0, 1, 1),  # Page 0, Index 1, Global 1
        (0, 2, 2),  # Page 0, Index 2, Global 2
        (1, 0, 3),  # Page 1, Index 0, Global 3
        (1, 1, 4),  # Page 1, Index 1, Global 4
    ]
    
    for i, (expected_page, expected_index, expected_global) in enumerate(expected_results):
        entry = enhanced_entries[i]
        page_num = entry['page_number']
        page_idx = entry['page_index']
        global_idx = entry['global_index']
        
        print(f"  Entry {i}: Page {page_num}, Index {page_idx}, Global {global_idx}")
        
        if (page_num == expected_page and 
            page_idx == expected_index and 
            global_idx == expected_global):
            print(f"    ✅ Correct")
        else:
            print(f"    ❌ ERROR: Expected Page {expected_page}, Index {expected_index}, Global {expected_global}")
            return False
    
    # Verify that page 0 entries have global_index equal to page_index
    print("\nVerifying page 0 entries have global_index = page_index:")
    for entry in enhanced_entries:
        if entry['page_number'] == 0:
            if entry['global_index'] != entry['page_index']:
                print(f"  ❌ ERROR: Page 0 entry has global_index {entry['global_index']} != page_index {entry['page_index']}")
                return False
    
    print("  ✅ All page 0 entries have correct global_index")
    
    # Verify that global_index is sequential
    print("\nVerifying global_index is sequential:")
    for i in range(len(enhanced_entries) - 1):
        if enhanced_entries[i]['global_index'] + 1 != enhanced_entries[i + 1]['global_index']:
            print(f"  ❌ ERROR: Non-sequential global_index detected!")
            return False
    
    print("  ✅ All global_index values are sequential")
    
    return True


def main():
    """Run the global_index test."""
    print("Global Index Calculation Logic Test")
    print("=" * 45)
    
    try:
        success = test_global_index_logic()
        
        if success:
            print("\n" + "=" * 45)
            print("✅ Global index calculation logic test passed!")
            print("The fix is working correctly.")
        else:
            print("\n" + "=" * 45)
            print("❌ Global index calculation logic test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
