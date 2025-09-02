#!/usr/bin/env python3

import json
import os
import argparse


def merge_runons(input_file, output_file):
    """
    Merge run-on entries with their parent entries and renumber indices
    """
    print(f"Loading processed entries from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    print(f"Processing {len(entries)} entries for run-on merging...")
    
    merged_entries = []
    entry_mapping = {}  # Maps old global_index to new global_index
    new_global_index = 0
    
    i = 0
    while i < len(entries):
        current_entry = entries[i].copy()
        
        # If this is not a run-on entry, start a new merged entry
        if not current_entry.get("runOn", False):
            base_text = current_entry["text"]
            merged_text_parts = [base_text]
            
            # Record the mapping for the current entry
            entry_mapping[current_entry["global_index"]] = new_global_index
            
            # Look ahead for consecutive run-on entries
            j = i + 1
            while j < len(entries) and entries[j].get("runOn", False):
                runon_entry = entries[j]
                
                # Verify this run-on belongs to the current entry
                if runon_entry.get("runOnFromIndex") == current_entry["global_index"]:
                    merged_text_parts.append(runon_entry["text"])
                    # Record the mapping for the run-on entry
                    entry_mapping[runon_entry["global_index"]] = new_global_index
                    j += 1
                else:
                    # This run-on belongs to a different entry, stop merging
                    break
            
            # Create the merged entry
            merged_entry = current_entry.copy()
            merged_entry["text"] = " ".join(merged_text_parts)
            merged_entry["global_index"] = new_global_index
            merged_entry["page_index"] = len([e for e in merged_entries if e["page_number"] == current_entry["page_number"]])
            
            # Remove run-on specific fields
            if "runOn" in merged_entry:
                del merged_entry["runOn"]
            if "runOnFromIndex" in merged_entry:
                del merged_entry["runOnFromIndex"]
            
            merged_entries.append(merged_entry)
            new_global_index += 1
            
            # Skip the run-on entries we just processed
            i = j
            
            print(f"Merged entry {new_global_index-1}: '{merged_entry['text'][:80]}...' (combined {j-i+1} entries)")
        else:
            # This shouldn't happen if run-ons are properly ordered, but handle it
            print(f"Warning: Found orphaned run-on entry at index {i}: '{current_entry['text'][:50]}...'")
            # Skip orphaned run-ons
            i += 1
    
    # Renumber page_index for each page
    page_counters = {}
    for entry in merged_entries:
        page_num = entry["page_number"]
        if page_num not in page_counters:
            page_counters[page_num] = 0
        entry["page_index"] = page_counters[page_num]
        page_counters[page_num] += 1
    
    print(f"Writing merged entries to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_entries, f, ensure_ascii=False, indent=2)
    
    # Save the index mapping for reference
    mapping_file = output_file.replace('.json', '_index_mapping.json')
    print(f"Writing index mapping to {mapping_file}")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump({
            "description": "Maps original global_index to new merged global_index",
            "mapping": entry_mapping,
            "original_count": len(entries),
            "merged_count": len(merged_entries)
        }, f, ensure_ascii=False, indent=2)
    
    # Print summary
    runon_count = len(entries) - len(merged_entries)
    print(f"\nMerging complete!")
    print(f"Original entries: {len(entries)}")
    print(f"Merged entries: {len(merged_entries)}")
    print(f"Run-on entries merged: {runon_count}")
    print(f"Compression ratio: {len(merged_entries)/len(entries):.2%}")
    
    return merged_entries, entry_mapping


def main():
    parser = argparse.ArgumentParser(description="Merge run-on entries with their parent entries")
    parser.add_argument("input_file", help="Input JSON file with processed entries (containing runOn metadata)")
    parser.add_argument("-o", "--output", default="processed_merged.json", 
                       help="Output JSON file (default: processed_merged.json)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        return 1
        
    merge_runons(args.input_file, args.output)
    return 0


if __name__ == "__main__":
    exit(main())