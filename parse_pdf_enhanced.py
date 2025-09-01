#!/usr/bin/env python3
import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional, Callable
sys.path.append('.')

from dots_ocr.parser import DotsOCRParser


class EnhancedDotsOCRParser:
    """
    Enhanced DotsOCR Parser with page numbering, indexing, filtering, and merging capabilities.
    """
    
    def __init__(self, 
                 ip='localhost',
                 port=8000,
                 model_name='model',
                 temperature=0.1,
                 top_p=1.0,
                 max_completion_tokens=16384,
                 num_thread=64,
                 dpi=200,
                 output_dir="./output",
                 min_pixels=None,
                 max_pixels=None,
                 use_hf=False):
        
        self.parser = DotsOCRParser(
            ip=ip,
            port=port,
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            max_completion_tokens=max_completion_tokens,
            num_thread=num_thread,
            dpi=dpi,
            output_dir=output_dir,
            min_pixels=min_pixels,
            max_pixels=max_pixels,
            use_hf=use_hf
        )
        self.output_dir = output_dir
    
    def filter_entries(self, entries: List[Dict[str, Any]], 
                      exclude_categories: Optional[List[str]] = None,
                      include_categories: Optional[List[str]] = None,
                      min_text_length: int = 0,
                      custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        """
        Filter entries based on various criteria.
        
        Args:
            entries: List of entry dictionaries
            exclude_categories: Categories to exclude (e.g., ['Page-header', 'Page-footer'])
            include_categories: Categories to include (if specified, only these are kept)
            min_text_length: Minimum text length to keep an entry
            custom_filter: Custom filter function that takes an entry and returns bool
            
        Returns:
            Filtered list of entries
        """
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
            
            # Apply custom filter
            if custom_filter and not custom_filter(entry):
                continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def add_page_info(self, page_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add page numbers and sequential indices to all entries.
        
        Args:
            page_results: List of page result dictionaries from the parser
            
        Returns:
            List of enhanced entries with page numbers and indices
        """
        enhanced_entries = []
        global_index_counter = 0
        
        for page_result in page_results:
            page_no = page_result.get('page_no', 0)
            layout_info_path = page_result.get('layout_info_path')
            
            if not layout_info_path or not os.path.exists(layout_info_path):
                continue
            
            # Load the layout JSON for this page
            try:
                with open(layout_info_path, 'r', encoding='utf-8') as f:
                    page_entries = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load layout info for page {page_no}: {e}")
                continue
            
            # Add page number and sequential index to each entry
            for idx, entry in enumerate(page_entries):
                enhanced_entry = entry.copy()
                enhanced_entry['page_number'] = page_no
                enhanced_entry['page_index'] = idx
                enhanced_entry['global_index'] = global_index_counter
                enhanced_entries.append(enhanced_entry)
                global_index_counter += 1
        
        return enhanced_entries
    
    def sort_entries(self, entries: List[Dict[str, Any]], 
                    sort_by: str = 'page_and_index') -> List[Dict[str, Any]]:
        """
        Sort entries by specified criteria.
        
        Args:
            entries: List of entry dictionaries
            sort_by: Sorting method ('page_and_index', 'category', 'text', 'bbox_y')
            
        Returns:
            Sorted list of entries
        """
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
    
    def parse_pdf_enhanced(self, 
                          pdf_path: str,
                          output_dir: str,
                          start_page: Optional[int] = None,
                          end_page: Optional[int] = None,
                          prompt_mode: str = "prompt_layout_text_only",
                          exclude_categories: Optional[List[str]] = None,
                          include_categories: Optional[List[str]] = None,
                          min_text_length: int = 0,
                          custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
                          sort_by: str = 'page_and_index',
                          save_individual_pages: bool = True,
                          save_merged_output: bool = True) -> Dict[str, Any]:
        """
        Parse PDF with enhanced features including filtering, indexing, and merging.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Output directory
            start_page: Starting page number (0-based)
            end_page: Ending page number (0-based)
            prompt_mode: Prompt mode for the parser
            exclude_categories: Categories to exclude
            include_categories: Categories to include
            min_text_length: Minimum text length
            custom_filter: Custom filter function
            sort_by: Sorting method
            save_individual_pages: Whether to save individual page files
            save_merged_output: Whether to save merged output
            
        Returns:
            Dictionary containing parsing results and statistics
        """
        # Clear and recreate output directory for clean testing
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse PDF using the original parser
        print(f"Parsing PDF: {pdf_path}")
        page_results = self.parser.parse_file(
            pdf_path, 
            output_dir, 
            prompt_mode=prompt_mode,
            start_page=start_page,
            end_page=end_page
        )
        
        # Add page information to all entries
        print("Adding page numbers and indices...")
        all_entries = self.add_page_info(page_results)
        
        # Apply filters
        print("Applying filters...")
        filtered_entries = self.filter_entries(
            all_entries,
            exclude_categories=exclude_categories,
            include_categories=include_categories,
            min_text_length=min_text_length,
            custom_filter=custom_filter
        )
        
        # Sort entries
        print(f"Sorting entries by {sort_by}...")
        sorted_entries = self.sort_entries(filtered_entries, sort_by)
        
        # Save merged output
        if save_merged_output:
            merged_output_path = os.path.join(output_dir, 'merged_entries.json')
            with open(merged_output_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
            print(f"✅ Merged output saved to: {merged_output_path}")
        
        # Generate statistics
        stats = {
            'total_pages': len(page_results),
            'total_entries_before_filter': len(all_entries),
            'total_entries_after_filter': len(filtered_entries),
            'categories_found': list(set(entry.get('category', '') for entry in all_entries)),
            'categories_in_output': list(set(entry.get('category', '') for entry in filtered_entries)),
            'page_range': {
                'start': min((entry.get('page_number', 0) for entry in filtered_entries), default=0),
                'end': max((entry.get('page_number', 0) for entry in filtered_entries), default=0)
            }
        }
        
        # Save statistics
        stats_path = os.path.join(output_dir, 'parsing_stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Parsing completed!")
        print(f"📊 Statistics: {stats['total_entries_after_filter']} entries from {stats['total_pages']} pages")
        print(f"📁 Output directory: {output_dir}")
        
        return {
            'entries': sorted_entries,
            'stats': stats,
            'output_dir': output_dir
        }


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced DotsOCR PDF Parser with filtering, indexing, and merging capabilities"
    )
    
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("output_dir", type=str, help="Output directory")
    
    # Page range arguments
    parser.add_argument("--start-page", type=int, help="Starting page number (0-based)")
    parser.add_argument("--end-page", type=int, help="Ending page number (0-based)")
    
    # Filtering arguments
    parser.add_argument("--exclude-categories", nargs='+', 
                       help="Categories to exclude (e.g., Page-header Page-footer)")
    parser.add_argument("--include-categories", nargs='+', 
                       help="Categories to include (if specified, only these are kept)")
    parser.add_argument("--min-text-length", type=int, default=0,
                       help="Minimum text length to keep an entry")
    
    # Sorting arguments
    parser.add_argument("--sort-by", choices=['page_and_index', 'category', 'text', 'bbox_y'], 
                       default='page_and_index', help="Sorting method")
    
    # Output arguments
    parser.add_argument("--no-merged-output", action='store_true',
                       help="Don't save merged output file")
    parser.add_argument("--no-individual-pages", action='store_true',
                       help="Don't save individual page files")
    
    # Parser arguments
    parser.add_argument("--prompt-mode", default="prompt_layout_text_only",
                       help="Prompt mode for the parser")
    parser.add_argument("--ip", default="localhost", help="VLLM server IP")
    parser.add_argument("--port", type=int, default=8000, help="VLLM server port")
    parser.add_argument("--model-name", default="model", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature")
    parser.add_argument("--top-p", type=float, default=1.0, help="Top-p")
    parser.add_argument("--max-completion-tokens", type=int, default=65536, help="Max completion tokens")
    parser.add_argument("--num-thread", type=int, default=2, help="Number of threads")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for PDF processing")
    
    args = parser.parse_args()
    
    # Initialize enhanced parser
    enhanced_parser = EnhancedDotsOCRParser(
        ip=args.ip,
        port=args.port,
        model_name=args.model_name,
        temperature=args.temperature,
        top_p=args.top_p,
        max_completion_tokens=args.max_completion_tokens,
        num_thread=args.num_thread,
        dpi=args.dpi,
        output_dir=args.output_dir
    )
    
    # Parse PDF with enhanced features
    result = enhanced_parser.parse_pdf_enhanced(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir,
        start_page=args.start_page,
        end_page=args.end_page,
        prompt_mode=args.prompt_mode,
        exclude_categories=args.exclude_categories,
        include_categories=args.include_categories,
        min_text_length=args.min_text_length,
        sort_by=args.sort_by,
        save_individual_pages=not args.no_individual_pages,
        save_merged_output=not args.no_merged_output
    )
    
    print(f"\n🎉 Enhanced parsing completed successfully!")
    print(f"📄 Processed {result['stats']['total_pages']} pages")
    print(f"📝 Found {result['stats']['total_entries_before_filter']} total entries")
    print(f"✅ Output {result['stats']['total_entries_after_filter']} filtered entries")
    print(f"📂 Results saved to: {result['output_dir']}")


if __name__ == "__main__":
    main()
