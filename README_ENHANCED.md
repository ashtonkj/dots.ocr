# Enhanced DotsOCR PDF Parser

This enhanced version of the DotsOCR PDF parser adds powerful features for filtering, indexing, and merging PDF parsing results.

## Features

### 1. Page Numbering and Sequential Indexing
- **Page Number**: Each detected entry includes the page number it was found on
- **Page Index**: Sequential index within each page (0-based)
- **Global Index**: Sequential index across all pages

### 2. Advanced Filtering
- **Category-based filtering**: Include or exclude specific categories (e.g., Page-header, Page-footer, Text, etc.)
- **Text length filtering**: Filter entries based on minimum text length
- **Custom filters**: Define your own filtering logic with Python functions

### 3. Flexible Sorting
- **Page and Index**: Sort by page number, then by index within page (default)
- **Category**: Sort by category, then by page and index
- **Text**: Sort alphabetically by text content
- **Bounding Box Y**: Sort by vertical position on page

### 4. Merged Output
- **Single JSON file**: All entries from all pages merged into one file
- **Statistics**: Comprehensive parsing statistics and metadata
- **Sorted results**: Entries sorted according to your preferences

## Installation

The enhanced parser uses the same dependencies as the original DotsOCR parser. Make sure you have the original parser working first.

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Basic parsing with default settings
./parse_pdf_enhanced.sh document.pdf output/

# Parse specific pages
./parse_pdf_enhanced.sh document.pdf output/ --start-page 0 --end-page 5
```

#### Filtering Examples
```bash
# Exclude headers and footers
./parse_pdf_enhanced.sh document.pdf output/ --exclude-categories Page-header Page-footer

# Only include specific categories
./parse_pdf_enhanced.sh document.pdf output/ --include-categories Text Section-header

# Filter by minimum text length
./parse_pdf_enhanced.sh document.pdf output/ --min-text-length 10

# Combine multiple filters
./parse_pdf_enhanced.sh document.pdf output/ \
  --exclude-categories Page-header Page-footer \
  --min-text-length 5 \
  --sort-by category
```

#### Sorting Options
```bash
# Sort by page and index (default)
./parse_pdf_enhanced.sh document.pdf output/ --sort-by page_and_index

# Sort by category
./parse_pdf_enhanced.sh document.pdf output/ --sort-by category

# Sort by text content
./parse_pdf_enhanced.sh document.pdf output/ --sort-by text

# Sort by vertical position
./parse_pdf_enhanced.sh document.pdf output/ --sort-by bbox_y
```

### Programmatic Usage

#### Basic Example
```python
from parse_pdf_enhanced import EnhancedDotsOCRParser

# Initialize parser
enhanced_parser = EnhancedDotsOCRParser(
    ip='localhost',
    port=8000,
    model_name='model',
    num_thread=2,
    dpi=150,
    max_completion_tokens=65536
)

# Parse PDF
result = enhanced_parser.parse_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    start_page=0,
    end_page=5
)

# Access results
entries = result['entries']
stats = result['stats']
print(f"Processed {stats['total_pages']} pages")
print(f"Found {stats['total_entries_after_filter']} entries")
```

#### Filtering Examples
```python
# Exclude specific categories
result = enhanced_parser.parse_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    exclude_categories=['Page-header', 'Page-footer'],
    min_text_length=5
)

# Include only specific categories
result = enhanced_parser.parse_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    include_categories=['Text', 'Section-header']
)

# Custom filter function
def custom_filter(entry):
    """Only keep text entries with Chinese characters"""
    import re
    if entry.get('category') != 'Text':
        return False
    text = entry.get('text', '')
    return bool(re.search(r'[\u4e00-\u9fff]', text))

result = enhanced_parser.parse_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    custom_filter=custom_filter
)
```

## Output Structure

### Enhanced Entry Format
Each entry in the output includes additional fields:

```json
{
  "bbox": [x1, y1, x2, y2],
  "category": "Text",
  "text": "Entry content...",
  "page_number": 0,
  "page_index": 5,
  "global_index": 25
}
```

### Output Files
- `merged_entries.json`: All entries merged into a single file, sorted according to your preferences
- `parsing_stats.json`: Comprehensive statistics about the parsing process
- Individual page files (if not disabled): Original page-by-page output

### Statistics File
```json
{
  "total_pages": 5,
  "total_entries_before_filter": 150,
  "total_entries_after_filter": 120,
  "categories_found": ["Text", "Section-header", "Page-header", "Page-footer"],
  "categories_in_output": ["Text", "Section-header"],
  "page_range": {
    "start": 0,
    "end": 4
  }
}
```

## Available Categories

The parser can detect various content categories:
- `Text`: Regular text content (including dictionary entries, glossaries, word lists)
- `Section-header`: Section headings
- `Page-header`: Page headers
- `Page-footer`: Page footers
- `Picture`: Images and graphics
- `Formula`: Mathematical formulas
- `List-item`: List items
- `Caption`: Image captions
- `Footnote`: Footnotes
- `Title`: Document titles

**Note**: The default prompt mode (`prompt_layout_text_only_no_tables`) is specifically optimized for dictionary content and will classify structured text (like dictionary entries) as `Text` rather than `Table` to avoid HTML formatting issues.

## Advanced Features

### Custom Filter Functions
You can define custom filter functions for complex filtering logic:

```python
def complex_filter(entry):
    """Custom filter with multiple conditions"""
    # Must be text entry
    if entry.get('category') != 'Text':
        return False
    
    text = entry.get('text', '')
    
    # Must contain certain keywords
    keywords = ['martial', 'arts', 'technique']
    if not any(keyword in text.lower() for keyword in keywords):
        return False
    
    # Must be longer than 20 characters
    if len(text) < 20:
        return False
    
    return True

result = enhanced_parser.parse_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    custom_filter=complex_filter
)
```

### Batch Processing
For processing multiple documents:

```python
import os
from parse_pdf_enhanced import EnhancedDotsOCRParser

enhanced_parser = EnhancedDotsOCRParser(
    ip='localhost',
    port=8000,
    model_name='model',
    num_thread=2,
    dpi=150
)

pdf_directory = "pdfs/"
output_base = "output/"

for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, filename)
        output_dir = os.path.join(output_base, filename[:-4])
        
        result = enhanced_parser.parse_pdf_enhanced(
            pdf_path=pdf_path,
            output_dir=output_dir,
            exclude_categories=['Page-header', 'Page-footer'],
            min_text_length=10
        )
        
        print(f"Processed {filename}: {result['stats']['total_entries_after_filter']} entries")
```

## Examples

Run the example script to see various usage patterns:

```bash
python example_enhanced_usage.py
```

This will demonstrate:
- Basic usage
- Filtering examples
- Custom filter functions
- Different sorting methods
- Category-specific filtering

## Command Line Options

### Required Arguments
- `pdf_path`: Path to the PDF file
- `output_dir`: Output directory for results

### Optional Arguments
- `--start-page <num>`: Starting page number (0-based)
- `--end-page <num>`: Ending page number (0-based)
- `--exclude-categories <list>`: Categories to exclude (space-separated)
- `--include-categories <list>`: Categories to include (space-separated)
- `--min-text-length <num>`: Minimum text length to keep
- `--sort-by <method>`: Sorting method (page_and_index, category, text, bbox_y)
- `--no-merged-output`: Don't save merged output file
- `--no-individual-pages`: Don't save individual page files

### Parser Configuration
- `--prompt-mode`: Prompt mode for the parser (default: prompt_layout_text_only_no_tables - optimized for dictionary content)
- `--ip`: VLLM server IP (default: localhost)
- `--port`: VLLM server port (default: 8000)
- `--model-name`: Model name (default: model)
- `--temperature`: Temperature for generation (default: 0.1)
- `--top-p`: Top-p for generation (default: 1.0)
- `--max-completion-tokens`: Max completion tokens (default: 65536)
- `--num-thread`: Number of threads (default: 2)
- `--dpi`: DPI for PDF processing (default: 150)

## Troubleshooting

### Common Issues

1. **VLLM server not running**: Make sure the VLLM server is running on the specified IP and port
2. **Memory issues**: Reduce `num_thread` and `max_completion_tokens` for large documents
3. **Filter not working**: Check that category names match exactly (case-sensitive)
4. **No output**: Verify that the PDF path is correct and the file exists

### Performance Tips

- Use `--num-thread 1` for memory-constrained systems
- Reduce `--dpi` for faster processing (at the cost of quality)
- Use `--min-text-length` to filter out noise
- Exclude unnecessary categories to reduce output size

## Migration from Original Parser

The enhanced parser is fully compatible with the original parser. To migrate:

1. Replace `parse_pdf.py` calls with `parse_pdf_enhanced.py`
2. Add filtering and sorting parameters as needed
3. Update output processing to use the new merged format

The enhanced parser maintains all original functionality while adding the new features.
