#!/usr/bin/env python3
import sys
import os
import json
sys.path.append('.')

from dots_ocr.parser import DotsOCRParser
from dots_ocr.utils.doc_utils import load_images_from_pdf

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse_pdf_safe.py <pdf_path> <output_dir> [--start-page N] [--end-page N]")
        print("Examples:")
        print("  python parse_pdf_safe.py doc.pdf ./output")
        print("  python parse_pdf_safe.py doc.pdf ./output --start-page 5")
        print("  python parse_pdf_safe.py doc.pdf ./output --start-page 5 --end-page 10")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Parse optional page range arguments
    start_page = 0
    end_page = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--start-page' and i + 1 < len(sys.argv):
            start_page = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--end-page' and i + 1 < len(sys.argv):
            end_page = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 Processing PDF: {pdf_path}")
    print(f"📁 Output directory: {output_dir}")
    if start_page > 0 or end_page is not None:
        print(f"�� Page range: {start_page} to {end_page if end_page else 'end'}")
    
    # Use only 2 threads to prevent memory issues
    parser = DotsOCRParser(
        ip='localhost',
        port=8000,
        model_name='model',
        output_dir=output_dir,
        num_thread=8,  # Much safer than 64
        dpi=150,       # Lower DPI to save memory
        max_completion_tokens=65536  # Reduce token limit
    )
    
    # Load only the specified page range
    if start_page > 0 or end_page is not None:
        print(f"🔄 Loading pages {start_page} to {end_page if end_page else 'end'}...")
        images_origin = load_images_from_pdf(pdf_path, dpi=parser.dpi, start_page_id=start_page, end_page_id=end_page)
        total_pages = len(images_origin)
        print(f"📄 Loaded {total_pages} pages")
        
        # Create tasks for only the loaded pages
        tasks = [
            {
                "origin_image": image,
                "prompt_mode": "prompt_layout_all_en",
                "save_dir": parser.output_dir,
                "save_name": os.path.splitext(os.path.basename(pdf_path))[0],
                "source": "pdf",
                "page_idx": start_page + i,  # Maintain correct page numbering
            } for i, image in enumerate(images_origin)
        ]

        def _execute_task(task_args):
            return parser._parse_single_image(**task_args)
        
        # Process the tasks
        results = []
        for i, task in enumerate(tasks):
            print(f"🔄 Processing page {start_page + i + 1}...")
            result = parser._parse_single_image(**task)
            results.append(result)
        
        # Update file paths
        for result in results:
            result['file_path'] = pdf_path
        
        # Save results
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        save_dir = os.path.join(output_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        
        # Save individual page results
        for result in results:
            page_save_dir = os.path.join(save_dir, f"page_{result['page_no']}")
            os.makedirs(page_save_dir, exist_ok=True)
            
            # Save layout image if it exists
            if 'layout_image' in result and result['layout_image']:
                layout_path = os.path.join(page_save_dir, 'layout_image.png')
                result['layout_image'].save(layout_path)
            
            # Save cells data
            if 'cells_data' in result:
                cells_path = os.path.join(page_save_dir, 'cells_data.json')
                with open(cells_path, 'w', encoding='utf-8') as f:
                    json.dump(result['cells_data'], f, ensure_ascii=False, indent=2)
        
        # Save combined results
        output_file = os.path.join(output_dir, f"{filename}_pages_{start_page}-{end_page if end_page else 'end'}.jsonl")
        with open(output_file, 'w', encoding="utf-8") as w:
            for result in results:
                w.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"✅ PDF parsed safely! Filtered results saved to: {output_file}")
        print(f"📄 Processed {len(results)} pages out of range {start_page} to {end_page if end_page else 'end'}")
        
    else:
        # Process all pages normally
        results = parser.parse_file(
            input_path=pdf_path,
            output_dir=output_dir,
            prompt_mode="prompt_layout_all_en"
        )
        print(f"✅ PDF parsed safely! Results saved to: {output_dir}")
        print(f"📄 Total pages processed: {len(results)}")