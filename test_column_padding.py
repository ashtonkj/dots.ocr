#!/usr/bin/env python3
"""
Test script to demonstrate column splitting with padding to avoid cutting off words.
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
sys.path.append('.')

from parse_pdf_enhanced import EnhancedDotsOCRParser


def create_test_page_with_words_near_line():
    """Create a test page image with words close to the vertical line."""
    # Create a test image (800x600 pixels)
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a vertical line in the middle
    line_x = width // 2
    draw.line([(line_x, 0), (line_x, height)], fill='black', width=2)
    
    # Add text that extends close to the line
    # Left column content with words near the line
    left_text = [
        "挨 (rad.64) āi 1. To be or get close to.",
        "āi shēn pào 挨身炮 Close Range Barrage",
        "矮 (rad.111) ǎi Short of stature; low.",
        "ǎi gōng bù 矮弓步 Low bow stance",
        "This text extends very close to the line on the left side"
    ]
    
    # Right column content with words near the line
    right_text = [
        "安 (rad.40) ān 1. Peaceful, calm.",
        "ān shēn pào 安身炮 Keep the Body Safe",
        "按 (rad.64) àn 1. To push down",
        "àn dào 按刀 Press down with a broadsword",
        "This text starts very close to the line on the right side"
    ]
    
    # Draw left column text (extending close to the line)
    y_offset = 50
    for text in left_text:
        # Position text so it extends close to the line
        text_x = 20
        if "extends very close" in text:
            text_x = line_x - 150  # Very close to the line
        draw.text((text_x, y_offset), text, fill='black')
        y_offset += 30
    
    # Draw right column text (starting close to the line)
    y_offset = 50
    for text in right_text:
        # Position text so it starts close to the line
        text_x = line_x + 20
        if "starts very close" in text:
            text_x = line_x + 5  # Very close to the line
        draw.text((text_x, y_offset), text, fill='black')
        y_offset += 30
    
    return image


def test_column_padding():
    """Test the column splitting with different padding values."""
    print("Testing Column Splitting with Padding")
    print("=" * 40)
    
    # Create test image
    test_image = create_test_page_with_words_near_line()
    
    # Save test image
    test_image_path = "test_page_with_words_near_line.png"
    test_image.save(test_image_path)
    print(f"Created test image: {test_image_path}")
    
    # Test the enhanced parser's line detection
    enhanced_parser = EnhancedDotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        num_thread=2,
        dpi=150
    )
    
    # Detect the vertical line
    line_x = enhanced_parser.detect_vertical_line(test_image)
    
    if line_x is None:
        print("❌ No vertical line detected")
        return False
    
    print(f"✅ Vertical line detected at x = {line_x}")
    
    # Test different padding values
    padding_values = [0, 10, 20, 30, 50]
    
    for padding in padding_values:
        print(f"\nTesting with {padding}px padding:")
        
        # Split columns with padding
        left_column, right_column = enhanced_parser.split_page_into_columns(test_image, line_x, padding)
        
        print(f"  Left column: {left_column.width} x {left_column.height}")
        print(f"  Right column: {right_column.width} x {right_column.height}")
        
        # Save the split columns
        left_filename = f"test_left_column_{padding}px_padding.png"
        right_filename = f"test_right_column_{padding}px_padding.png"
        left_column.save(left_filename)
        right_column.save(right_filename)
        print(f"  Saved: {left_filename}, {right_filename}")
        
        # Calculate overlap/gap
        total_width = left_column.width + right_column.width
        original_width = test_image.width
        overlap = total_width - original_width
        
        if overlap > 0:
            print(f"  ✅ Overlap: {overlap}px (ensures no text is cut off)")
        elif overlap < 0:
            print(f"  ⚠️  Gap: {abs(overlap)}px (gap between columns - may cut text)")
        else:
            print(f"  ✅ Perfect fit: no overlap or gap")
    
    return True


def test_real_data_with_padding():
    """Test column splitting with real data using different padding values."""
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
            dpi=150
        )
        
        # Test with different padding values
        padding_values = [10, 20, 30]
        
        for padding in padding_values:
            print(f"\nTesting with {padding}px padding on page 20...")
            
            result = enhanced_parser.parse_pdf_enhanced(
                pdf_path=pdf_path,
                output_dir=f"/home/kevin/development/parsed/column_test_{padding}px",
                start_page=20,
                end_page=20,
                use_column_splitting=True,
                column_padding=padding
            )
            
            print(f"  ✅ Completed with {padding}px padding!")
            print(f"  Processed {result['stats']['total_pages']} pages")
            print(f"  Found {result['stats']['total_entries_before_filter']} entries")
            print(f"  Columns: {result['stats']['columns_processed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing with real data: {e}")
        return False


def main():
    """Run column padding tests."""
    print("Column Splitting with Padding Test")
    print("=" * 50)
    
    # Test 1: Basic padding functionality
    success1 = test_column_padding()
    
    # Test 2: Real data test (if available)
    success2 = test_real_data_with_padding()
    
    print("\n" + "=" * 50)
    if success1:
        print("✅ Column padding test passed!")
    else:
        print("❌ Column padding test failed!")
    
    if success2:
        print("✅ Real data padding test passed!")
    else:
        print("⚠️  Real data padding test skipped or failed")
    
    print("\nUsage:")
    print("  ./parse_pdf_enhanced.sh document.pdf output/                    # Default 20px padding")
    print("  ./parse_pdf_enhanced.sh document.pdf output/ --column-padding 30 # 30px padding")
    print("  ./parse_pdf_enhanced.sh document.pdf output/ --column-padding 10 # 10px padding")


if __name__ == "__main__":
    main()
