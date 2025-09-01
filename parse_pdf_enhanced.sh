#!/bin/bash

# Enhanced PDF parsing script with filtering, indexing, and merging capabilities
# Usage: ./parse_pdf_enhanced.sh <pdf_path> <output_dir> [options]

# Check if we're in merge-only mode
MERGE_ONLY=false
for arg in "$@"; do
    if [ "$arg" = "--merge-only" ]; then
        MERGE_ONLY=true
        break
    fi
done

# Check if we have enough arguments
if [ "$MERGE_ONLY" = true ]; then
    # In merge-only mode, we need at least 1 argument (output directory)
    if [ $# -lt 1 ]; then
        echo "Error: Output directory is required for merge-only mode"
        echo "Usage: $0 <output_dir> --merge-only [options]"
        exit 1
    fi
else
    # In normal mode, we need at least 2 arguments (PDF path and output directory)
    if [ $# -lt 2 ]; then
        echo "Usage: $0 <pdf_path> <output_dir> [options]"
        echo ""
        echo "Required arguments:"
        echo "  pdf_path    Path to the PDF file"
        echo "  output_dir  Output directory for results"
        echo ""
        echo "Optional arguments:"
        echo "  --start-page <num>           Starting page number (0-based)"
        echo "  --end-page <num>             Ending page number (0-based)"
        echo "  --exclude-categories <list>  Categories to exclude (space-separated)"
        echo "  --include-categories <list>  Categories to include (space-separated)"
        echo "  --min-text-length <num>      Minimum text length to keep"
        echo "  --sort-by <method>           Sorting method (page_and_index, category, text, bbox_y)"
        echo "  --no-merged-output           Don't save merged output file"
        echo "  --no-individual-pages        Don't save individual page files"
        echo "  --no-column-splitting        Disable column splitting (process full pages)"
        echo "  --no-clear-output            Don't clear output directory before processing (default: clear)"
        echo "  --merge-only                 Only merge and filter existing JSON files (skip PDF parsing)"
        echo "  --column-padding <num>       Padding around vertical line when splitting (default: 20px)"
        echo ""
        echo "Examples:"
        echo "  $0 document.pdf output/ --start-page 0 --end-page 5"
        echo "  $0 document.pdf output/ --exclude-categories Page-header Page-footer"
        echo "  $0 document.pdf output/ --include-categories Text Section-header"
        echo "  $0 document.pdf output/ --min-text-length 10 --sort-by category"
        echo "  $0 document.pdf output/ --no-column-splitting  # Process full pages without splitting"
        echo "  $0 document.pdf output/ --no-clear-output      # Don't clear output directory before processing"
        echo "  $0 output/ --merge-only                        # Only merge existing JSON files (no PDF parsing)"
        echo "  $0 document.pdf output/ --column-padding 30    # Use 30px padding around vertical line"
        exit 1
    fi
fi

if [ "$MERGE_ONLY" = true ]; then
    # In merge-only mode, first argument is output directory
    OUTPUT_DIR="$1"
    shift 1
    CMD="python parse_pdf_enhanced.py \"$OUTPUT_DIR\""
else
    # Normal mode, first argument is PDF path, second is output directory
    PDF_PATH="$1"
    OUTPUT_DIR="$2"
    shift 2
    CMD="python parse_pdf_enhanced.py \"$PDF_PATH\" \"$OUTPUT_DIR\""
fi

# Add all remaining arguments
while [ $# -gt 0 ]; do
    CMD="$CMD $1"
    shift
done

echo "Running enhanced PDF parser..."
echo "Command: $CMD"
echo ""

# Execute the command
eval $CMD
