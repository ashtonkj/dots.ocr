#!/usr/bin/env python3

import json
import os
import argparse


def json_to_markdown(input_file, output_file):
    """
    Convert processed merged JSON to markdown file containing only text content
    """
    print(f"Loading merged entries from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    print(f"Converting {len(entries)} entries to markdown...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            # Write the text content
            f.write(entry.get("text", ""))
            
            # Add blank line between entries (except for the last entry)
            if i < len(entries) - 1:
                f.write("\n\n")
            else:
                f.write("\n")
    
    print(f"Markdown file written to {output_file}")
    print(f"Total entries: {len(entries)}")
    
    # Calculate file size
    file_size = os.path.getsize(output_file)
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Convert processed merged JSON to markdown text file")
    parser.add_argument("input_file", help="Input JSON file with processed merged entries")
    parser.add_argument("-o", "--output", default="dictionary.md", 
                       help="Output markdown file (default: dictionary.md)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        return 1
        
    json_to_markdown(args.input_file, args.output)
    return 0


if __name__ == "__main__":
    exit(main())