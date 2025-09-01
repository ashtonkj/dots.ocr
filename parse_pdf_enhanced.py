#!/usr/bin/env python3
import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional, Callable
from PIL import Image, ImageDraw
import numpy as np
sys.path.append('.')

from dots_ocr.parser import DotsOCRParser


class EnhancedDotsOCRParser:
    """
    Enhanced DotsOCR Parser with page numbering, indexing, filtering, merging capabilities,
    and column splitting for dictionary content.
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
    
    def detect_vertical_line(self, image: Image.Image, threshold: int = 10) -> Optional[int]:
        """
        Detect the vertical line that separates columns in the page.
        
        Args:
            image: PIL Image of the page
            threshold: Minimum number of black pixels to consider a line
        
        Returns:
            x-coordinate of the vertical line, or None if not found
        """
        # Convert to grayscale and get pixel data
        gray = image.convert('L')
        pixels = np.array(gray)
        
        # Look for vertical lines by checking each x-coordinate
        height, width = pixels.shape
        mid_x = width // 2
        
        # Search around the middle of the page
        search_range = width // 4  # Search in the middle half
        start_x = mid_x - search_range // 2
        end_x = mid_x + search_range // 2
        
        best_line_x = None
        max_black_pixels = 0
        
        for x in range(start_x, end_x):
            # Count black pixels in this vertical line
            black_pixels = np.sum(pixels[:, x] < 128)  # Assuming black pixels are < 128
            
            if black_pixels > max_black_pixels and black_pixels > threshold:
                max_black_pixels = black_pixels
                best_line_x = x
        
        return best_line_x
    
    def split_page_into_columns(self, image: Image.Image, line_x: int, padding: int = 20) -> tuple[Image.Image, Image.Image]:
        """
        Split a page image into left and right columns with padding around the line.
        
        Args:
            image: PIL Image of the full page
            line_x: x-coordinate of the vertical line
            padding: Number of pixels to add on each side of the line to avoid cutting words
        
        Returns:
            Tuple of (left_column_image, right_column_image)
        """
        width, height = image.size
        
        # Calculate split points with padding
        # Left column extends to line + padding (captures text near the line)
        left_split_x = line_x + padding
        # Right column starts from line - padding (captures text near the line)
        right_split_x = line_x - padding
        
        # Ensure we don't go outside image bounds
        left_split_x = min(width, left_split_x)
        right_split_x = max(0, right_split_x)
        
        # Create left column (from left edge to line + padding)
        left_column = image.crop((0, 0, left_split_x, height))
        
        # Create right column (from line - padding to right edge)
        right_column = image.crop((right_split_x, 0, width, height))
        
        return left_column, right_column
    
    def process_page_with_columns(self, page_image: Image.Image, page_no: int, 
                                prompt_mode: str, save_dir: str, filename: str, 
                                column_padding: int = 20) -> List[Dict[str, Any]]:
        """
        Process a single page by splitting it into columns and processing each column separately.
        
        Args:
            page_image: PIL Image of the full page
            page_no: Page number
            prompt_mode: Prompt mode for the parser
            save_dir: Directory to save results
            filename: Base filename for the page
        
        Returns:
            List of enhanced entries from both columns
        """
        # Detect the vertical line
        line_x = self.detect_vertical_line(page_image)
        
        if line_x is None:
            print(f"Warning: No vertical line detected on page {page_no}, processing as single column")
            # Process the entire page as one column
            result = self.parser._parse_single_image(
                page_image, prompt_mode, save_dir, f"{filename}_page_{page_no}", 
                source="pdf", page_idx=page_no
            )
            result['column'] = "full"
            return [result]
        
        # Split the page into columns
        left_column, right_column = self.split_page_into_columns(page_image, line_x, column_padding)
        
        print(f"Page {page_no}: Split at x={line_x} (padding: {column_padding}px), left width={left_column.width}, right width={right_column.width}")
        
        # Process left column
        left_result = self.parser._parse_single_image(
            left_column, prompt_mode, save_dir, f"{filename}_page_{page_no}_left", 
            source="pdf", page_idx=page_no
        )
        left_result['column'] = "left"
        
        # Process right column
        right_result = self.parser._parse_single_image(
            right_column, prompt_mode, save_dir, f"{filename}_page_{page_no}_right", 
            source="pdf", page_idx=page_no
        )
        right_result['column'] = "right"
        
        return [left_result, right_result]
    
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
        Add page numbers and page indices to all entries (global indices assigned later).
        
        Args:
            page_results: List of page result dictionaries from the parser
            
        Returns:
            List of enhanced entries with page numbers and page indices
        """
        enhanced_entries = []
        
        for page_result in page_results:
            page_no = page_result.get('page_no', 0)
            column = page_result.get('column', 'full')  # 'left', 'right', or 'full'
            layout_info_path = page_result.get('layout_info_path')
            
            if not layout_info_path or not os.path.exists(layout_info_path):
                continue
            
            # Load the layout JSON for this page/column
            try:
                with open(layout_info_path, 'r', encoding='utf-8') as f:
                    page_entries = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load layout info for page {page_no} column {column}: {e}")
                continue
            
            # Add page information to each entry
            for idx, entry in enumerate(page_entries):
                # Skip entries that are not dictionaries (e.g., strings, numbers, etc.)
                if not isinstance(entry, dict):
                    print(f"Warning: Skipping non-dict entry at page {page_no} column {column} index {idx}: {type(entry)} - {entry}")
                    continue
                
                enhanced_entry = entry.copy()
                enhanced_entry['page_number'] = page_no
                enhanced_entry['page_index'] = idx
                enhanced_entry['column'] = column
                enhanced_entries.append(enhanced_entry)
        
        return enhanced_entries
    
    def load_existing_json_files(self, output_dir: str) -> List[Dict[str, Any]]:
        """
        Load all existing JSON files from the output directory and merge them.
        
        Args:
            output_dir: Output directory containing JSON files
            
        Returns:
            List of enhanced entries with page numbers and page indices (global indices assigned later)
        """
        enhanced_entries = []
        
        # Find all JSON files in the output directory
        json_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json') and not file.startswith('merged_'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            print(f"Warning: No JSON files found in {output_dir}")
            return enhanced_entries
        
        print(f"Found {len(json_files)} JSON files to merge")
        
        # Sort files by page number (numeric) to ensure correct ordering
        def extract_page_number(filepath):
            filename = os.path.basename(filepath)
            import re
            page_match = re.search(r'_page_(\d+)_', filename)
            if page_match:
                return int(page_match.group(1))
            return 0  # Default to 0 if no page number found
        
        json_files.sort(key=extract_page_number)
        
        # Debug: Show the sorted order
        print("Processing files in order:")
        for i, json_file in enumerate(json_files[:5]):  # Show first 5 files
            page_num = extract_page_number(json_file)
            print(f"  {i+1}. Page {page_num}: {os.path.basename(json_file)}")
        if len(json_files) > 5:
            print(f"  ... and {len(json_files) - 5} more files")
        
        for json_file in json_files:
            try:
                # Extract page and column info from filename
                filename = os.path.basename(json_file)
                page_no = 0
                column = 'full'
                
                # Parse filename to extract page number and column
                # Expected format: *_page_<num>_<column>_page_<num>.json
                import re
                page_match = re.search(r'_page_(\d+)_', filename)
                if page_match:
                    page_no = int(page_match.group(1))
                
                column_match = re.search(r'_page_\d+_(left|right)_', filename)
                if column_match:
                    column = column_match.group(1)
                
                # Load the JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    page_entries = json.load(f)
                
                # Add page information to each entry
                for idx, entry in enumerate(page_entries):
                    # Skip entries that are not dictionaries (e.g., strings, numbers, etc.)
                    if not isinstance(entry, dict):
                        print(f"Warning: Skipping non-dict entry in {filename} at index {idx}: {type(entry)} - {entry}")
                        continue
                    
                    enhanced_entry = entry.copy()
                    enhanced_entry['page_number'] = page_no
                    enhanced_entry['page_index'] = idx
                    enhanced_entry['column'] = column
                    enhanced_entries.append(enhanced_entry)
                
                print(f"Loaded {len(page_entries)} entries from {filename}")
                
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
                continue
        
        print(f"Total entries loaded: {len(enhanced_entries)}")
        return enhanced_entries
    
    def assign_global_indices(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign contiguous global indices to entries after filtering.
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            List of entries with updated global indices
        """
        for idx, entry in enumerate(entries):
            entry['global_index'] = idx
        return entries
    
    def merge_and_filter_only(self,
                             output_dir: str,
                             exclude_categories: Optional[List[str]] = None,
                             include_categories: Optional[List[str]] = None,
                             min_text_length: int = 0,
                             custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
                             sort_by: str = 'page_and_index',
                             save_merged_output: bool = True) -> Dict[str, Any]:
        """
        Merge and filter existing JSON files in the output directory without parsing PDF.
        
        Args:
            output_dir: Output directory containing JSON files
            exclude_categories: Categories to exclude
            include_categories: Categories to include
            min_text_length: Minimum text length
            custom_filter: Custom filter function
            sort_by: Sorting method
            save_merged_output: Whether to save merged output
            
        Returns:
            Dictionary containing merge results and statistics
        """
        print("🔄 Merge-only mode: Loading existing JSON files...")
        
        # Load all existing JSON files
        all_entries = self.load_existing_json_files(output_dir)
        
        if not all_entries:
            print("❌ No entries found to merge")
            return {
                'stats': {
                    'total_pages': 0,
                    'total_entries_before_filter': 0,
                    'total_entries_after_filter': 0,
                    'categories_found': [],
                    'categories_in_output': [],
                    'page_range': {'start': 0, 'end': 0},
                    'columns_processed': []
                },
                'output_dir': output_dir
            }
        
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
        
        # Assign contiguous global indices after filtering and sorting
        print("Assigning global indices...")
        sorted_entries = self.assign_global_indices(sorted_entries)
        
        # Save merged output
        if save_merged_output:
            merged_output_path = os.path.join(output_dir, 'merged_entries.json')
            with open(merged_output_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
            print(f"✅ Merged output saved to: {merged_output_path}")
        
        # Generate statistics
        stats = {
            'total_pages': len(set(entry.get('page_number', 0) for entry in all_entries)),
            'total_entries_before_filter': len(all_entries),
            'total_entries_after_filter': len(filtered_entries),
            'categories_found': list(set(entry.get('category', '') for entry in all_entries)),
            'categories_in_output': list(set(entry.get('category', '') for entry in filtered_entries)),
            'page_range': {
                'start': min((entry.get('page_number', 0) for entry in filtered_entries), default=0),
                'end': max((entry.get('page_number', 0) for entry in filtered_entries), default=0)
            },
            'columns_processed': list(set(entry.get('column', 'full') for entry in filtered_entries))
        }
        
        return {
            'stats': stats,
            'output_dir': output_dir,
            'merged_entries': sorted_entries
        }
    
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
            return sorted(entries, key=lambda x: (x.get('page_number', 0), x.get('column', 'full'), x.get('page_index', 0)))
        elif sort_by == 'category':
            return sorted(entries, key=lambda x: (x.get('category', ''), x.get('page_number', 0), x.get('column', 'full'), x.get('page_index', 0)))
        elif sort_by == 'text':
            return sorted(entries, key=lambda x: (x.get('text', '').lower(), x.get('page_number', 0), x.get('column', 'full'), x.get('page_index', 0)))
        elif sort_by == 'bbox_y':
            return sorted(entries, key=lambda x: (x.get('page_number', 0), x.get('column', 'full'), x.get('bbox', [0, 0, 0, 0])[1]))
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
                          save_merged_output: bool = True,
                          use_column_splitting: bool = True,
                          column_padding: int = 20,
                          clear_output: bool = True) -> Dict[str, Any]:
        """
        Parse PDF with enhanced features including filtering, indexing, merging, and column splitting.
        
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
            use_column_splitting: Whether to split pages into columns before processing
            column_padding: Number of pixels to extend each column around the vertical line (creates overlap to prevent word cutting)
            clear_output: Whether to clear the output directory before processing (default: True)
            
        Returns:
            Dictionary containing parsing results and statistics
        """
        # Clear and recreate output directory for clean testing (if requested)
        import shutil
        if clear_output and os.path.exists(output_dir):
            print(f"Clearing output directory: {output_dir}")
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        if use_column_splitting:
            # Use custom column-splitting approach
            print(f"Parsing PDF with column splitting: {pdf_path}")
            page_results = self._parse_pdf_with_columns(
                pdf_path, output_dir, prompt_mode, start_page, end_page, column_padding
            )
        else:
            # Use original parser approach
            print(f"Parsing PDF with original method: {pdf_path}")
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
        
        # Assign contiguous global indices after filtering and sorting
        print("Assigning global indices...")
        sorted_entries = self.assign_global_indices(sorted_entries)
        
        # Save merged output
        if save_merged_output:
            merged_output_path = os.path.join(output_dir, 'merged_entries.json')
            with open(merged_output_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
            print(f"✅ Merged output saved to: {merged_output_path}")
        
        # Generate statistics
        stats = {
            'total_pages': len(set(result.get('page_no', 0) for result in page_results)),
            'total_entries_before_filter': len(all_entries),
            'total_entries_after_filter': len(filtered_entries),
            'categories_found': list(set(entry.get('category', '') for entry in all_entries)),
            'categories_in_output': list(set(entry.get('category', '') for entry in filtered_entries)),
            'page_range': {
                'start': min((entry.get('page_number', 0) for entry in filtered_entries), default=0),
                'end': max((entry.get('page_number', 0) for entry in filtered_entries), default=0)
            },
            'columns_processed': list(set(entry.get('column', 'full') for entry in filtered_entries))
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
    
    def _parse_pdf_with_columns(self, pdf_path: str, output_dir: str, prompt_mode: str,
                               start_page: Optional[int] = None, end_page: Optional[int] = None,
                               column_padding: int = 20) -> List[Dict[str, Any]]:
        """
        Parse PDF using column splitting approach.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Output directory
            prompt_mode: Prompt mode for the parser
            start_page: Starting page number (0-based)
            end_page: Ending page number (0-based)
            
        Returns:
            List of page result dictionaries
        """
        from dots_ocr.utils.doc_utils import load_images_from_pdf
        
        print(f"Loading PDF: {pdf_path}")
        images_origin = load_images_from_pdf(pdf_path, dpi=self.parser.dpi, start_page_id=start_page, end_page_id=end_page)
        total_pages = len(images_origin)
        
        filename, _ = os.path.splitext(os.path.basename(pdf_path))
        save_dir = os.path.join(output_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"Processing {total_pages} pages with column splitting...")
        
        all_results = []
        for i, image in enumerate(images_origin):
            page_no = start_page + i if start_page is not None else i
            print(f"Processing page {page_no}...")
            
            # Process this page with column splitting
            page_results = self.process_page_with_columns(
                image, page_no, prompt_mode, save_dir, filename, column_padding
            )
            
            all_results.extend(page_results)
        
        return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced DotsOCR PDF Parser with filtering, indexing, merging, and column splitting capabilities"
    )
    
    parser.add_argument("pdf_path", type=str, nargs='?', help="Path to the PDF file (optional when using --merge-only)")
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
    parser.add_argument("--no-column-splitting", action='store_true',
                       help="Disable column splitting and process full pages")
    parser.add_argument("--no-clear-output", action='store_true',
                       help="Don't clear the output directory before processing (default: clear output directory)")
    parser.add_argument("--merge-only", action='store_true',
                       help="Only merge and filter existing JSON files in output directory (skip PDF parsing)")
    parser.add_argument("--column-padding", type=int, default=20,
                       help="Padding to extend columns around vertical line (default: 20px, creates overlap)")
    
    # Parser arguments
    parser.add_argument("--prompt-mode", default="prompt_layout_text_only_no_tables",
                       help="Prompt mode for the parser (default: ultra-optimized for dictionary content)")
    parser.add_argument("--ip", default="localhost", help="VLLM server IP")
    parser.add_argument("--port", type=int, default=8000, help="VLLM server port")
    parser.add_argument("--model-name", default="model", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature")
    parser.add_argument("--top-p", type=float, default=1.0, help="Top-p")
    parser.add_argument("--max-completion-tokens", type=int, default=65536, help="Max completion tokens")
    parser.add_argument("--num-thread", type=int, default=4, help="Number of threads")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for PDF processing")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.merge_only and not args.pdf_path:
        parser.error("pdf_path is required when not using --merge-only mode")
    
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
    
    if args.merge_only:
        # Merge and filter only mode
        print("🔄 Running in merge-only mode...")
        result = enhanced_parser.merge_and_filter_only(
            output_dir=args.output_dir,
            exclude_categories=args.exclude_categories,
            include_categories=args.include_categories,
            min_text_length=args.min_text_length,
            sort_by=args.sort_by,
            save_merged_output=not args.no_merged_output
        )
        print(f"\n🎉 Merge and filter completed successfully!")
    else:
        # Full PDF parsing mode
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
            save_merged_output=not args.no_merged_output,
            use_column_splitting=not args.no_column_splitting,
            column_padding=args.column_padding,
            clear_output=not args.no_clear_output
        )
        print(f"\n🎉 Enhanced parsing completed successfully!")
    
    print(f"📄 Processed {result['stats']['total_pages']} pages")
    print(f"📝 Found {result['stats']['total_entries_before_filter']} total entries")
    print(f"✅ Output {result['stats']['total_entries_after_filter']} filtered entries")
    print(f"📂 Results saved to: {result['output_dir']}")


if __name__ == "__main__":
    main()
