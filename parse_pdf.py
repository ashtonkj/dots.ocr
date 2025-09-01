#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from dots_ocr.parser import DotsOCRParser

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse_pdf.py <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    start_page = None
    end_page = None
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--start-page':
            start_page = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--end-page':
            end_page = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Clear and recreate output directory for clean testing
    import shutil
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize parser
    parser = DotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        output_dir=output_dir,
        num_thread=2,  # Much safer than 64
        dpi=150,       # Lower DPI to save memory
        max_completion_tokens=65536  # Reduce token limit
    )
    
    # Parse PDF
    results = parser.parse_file(pdf_path, output_dir, start_page=start_page, end_page=end_page, prompt_mode="prompt_layout_text_only")
    print(f"✅ PDF parsed! Results saved to: {output_dir}")
