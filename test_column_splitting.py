#!/usr/bin/env python3
"""
Test script to demonstrate column splitting functionality.
"""

import sys
import os
from PIL import Image, ImageDraw
import numpy as np
sys.path.append('.')

from parse_pdf_enhanced import EnhancedDotsOCRParser


def create_test_page_with_columns():
    """Create a test page image with two columns separated by a vertical line."""
    # Create a test image (800x600 pixels)
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a vertical line in the middle
    line_x = width // 2
    draw.line([(line_x, 0), (line_x, height)], fill='black', width=2)
    
    # Add some sample text content
    # Left column content
    left_text = [
        "挨 (rad.64) āi 1. To be or get close to.",
        "āi shēn pào 挨身炮 Close Range Barrage",
        "矮 (rad.111) ǎi Short of stature; low.",
        "ǎi gōng bù 矮弓步 Low bow stance"
    ]
    
    # Right column content
    right_text = [
        "安 (rad.40) ān 1. Peaceful, calm.",
        "ān shēn pào 安身炮 Keep the Body Safe",
        "按 (rad.64) àn 1. To push down",
        "àn dào 按刀 Press down with a broadsword"
    ]
    
    # Draw left column text
    y_offset = 50
    for text in left_text:
        draw.text((20, y_offset), text, fill='black')
        y_offset += 30
    
    # Draw right column text
    y_offset = 50
    for text in right_text:
        draw.text((line_x + 20, y_offset), text, fill='black')
        y_offset += 30
    
    return image


def test_column_detection():
    """Test the vertical line detection functionality."""
    print("Testing Column Detection")
    print("=" * 30)
    
    # Create test image
    test_image = create_test_page_with_columns()
    
    # Save test image
    test_image_path = "test_page_with_columns.png"
    test_image.save(test_image_path)
    print(f"Created test image: {test_image_path}")
    
    # Test the enhanced parser's line detection
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=200
    )
    
    # Detect the vertical line
    line_x = enhanced_parser.detect_vertical_line(test_image)
    
    if line_x is not None:
        print(f"✅ Vertical line detected at x = {line_x}")
        print(f"   Expected: ~400, Actual: {line_x}")
        
        # Test column splitting
        left_column, right_column = enhanced_parser.split_page_into_columns(test_image, line_x)
        
        print(f"✅ Columns split successfully:")
        print(f"   Left column: {left_column.width} x {left_column.height}")
        print(f"   Right column: {right_column.width} x {right_column.height}")
        
        # Save the split columns
        left_column.save("test_left_column.png")
        right_column.save("test_right_column.png")
        print("   Saved: test_left_column.png, test_right_column.png")
        
    else:
        print("❌ No vertical line detected")
    
    return line_x is not None


def test_column_splitting_with_real_data():
    """Test column splitting with real PDF data if available."""
    print("\nTesting Column Splitting with Real Data")
    print("=" * 40)
    
    # Check if we have real data to test with
    pdf_path = "/home/kevin/Downloads/FalksDictionaryOfChineseMartialArts.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found at {pdf_path}")
        print("   Skipping real data test")
        return False
    
    try:
        enhanced_parser = EnhancedDotsOCRParser(
            ip='localhost',
            port=8000,
            model_name='model',
            num_thread=2,
            dpi=200
        )
        
        # Test with just one page
        print("Testing column splitting on page 20...")
        
        result = enhanced_parser.parse_pdf_enhanced(
            pdf_path=pdf_path,
            output_dir="/home/kevin/development/parsed/column_test",
            start_page=20,
            end_page=20,
            use_column_splitting=True
        )
        
        print(f"✅ Column splitting test completed!")
        print(f"   Processed {result['stats']['total_pages']} pages")
        print(f"   Found {result['stats']['total_entries_before_filter']} entries")
        print(f"   Columns: {result['stats']['columns_processed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing with real data: {e}")
        return False


def main():
    """Run column splitting tests."""
    print("Column Splitting Test")
    print("=" * 50)
    
    # Test 1: Basic column detection
    success1 = test_column_detection()
    
    # Test 2: Real data test (if available)
    success2 = test_column_splitting_with_real_data()
    
    print("\n" + "=" * 50)
    if success1:
        print("✅ Column detection test passed!")
    else:
        print("❌ Column detection test failed!")
    
    if success2:
        print("✅ Real data test passed!")
    else:
        print("⚠️  Real data test skipped or failed")
    
    print("\nUsage:")
    print("  ./parse_pdf_enhanced.sh document.pdf output/  # Uses column splitting by default")
    print("  ./parse_pdf_enhanced.sh document.pdf output/ --no-column-splitting  # Disable splitting")


if __name__ == "__main__":
    main()

