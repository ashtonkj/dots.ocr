#!/usr/bin/env python3

import json
import os
import argparse
from openai import OpenAI


def call_text_llm(text, ip="localhost", port=8000, model_name="model", temperature=0.1):
    """
    Call the LLM with text-only input to determine if an entry is a run-on
    """
    addr = f"http://{ip}:{port}/v1"
    client = OpenAI(api_key="{}".format(os.environ.get("API_KEY", "0")), base_url=addr)
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": text}],
            model=model_name,
            max_completion_tokens=10,
            temperature=0.0,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM request error: {e}")
        return None


def is_runon_entry(current_entry, previous_entry):
    """
    Use LLM to determine if current entry is a continuation of the previous entry
    """
    prompt = f"""Dictionary entry analysis:

COMPLETE entries have this format:
- Characters (Radical) Romanization Definition
- Romanization Characters Definition  

RUN-ON entries are incomplete fragments that continue the previous entry.

Previous: "{previous_entry}"
Current: "{current_entry}"

Is the current entry a run-on continuation? Answer YES or NO only."""

    response = call_text_llm(prompt)
    if response and "YES" in response.upper():
        return True
    return False


def process_runons(input_file, output_file, ip="localhost", port=8000, model_name="model"):
    """
    Process merged entries to detect run-ons and add runOn metadata
    """
    print(f"Loading entries from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    print(f"Processing {len(entries)} entries for run-on detection...")
    
    processed_entries = []
    
    for i, entry in enumerate(entries):
        # Initialize runOn fields
        entry["runOn"] = False
        entry["runOnFromIndex"] = None
        
        # Skip first entry or if no previous entry
        if i == 0:
            processed_entries.append(entry)
            continue
            
        previous_entry = entries[i-1]
        current_text = entry.get("text", "")
        previous_text = previous_entry.get("text", "")
        
        # Skip if either text is empty
        if not current_text or not previous_text:
            processed_entries.append(entry)
            continue
            
        print(f"Checking entry {i+1}/{len(entries)}: '{current_text[:50]}...'")
        
        # Use LLM to determine if this is a run-on
        if is_runon_entry(current_text, previous_text):
            entry["runOn"] = True
            entry["runOnFromIndex"] = previous_entry["global_index"]
            print(f"  -> Detected as run-on from index {previous_entry['global_index']}")
        else:
            print(f"  -> Independent entry")
        
        processed_entries.append(entry)
    
    print(f"Writing processed entries to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_entries, f, ensure_ascii=False, indent=2)
    
    # Print summary
    runon_count = sum(1 for entry in processed_entries if entry.get("runOn", False))
    print(f"\nProcessing complete!")
    print(f"Total entries: {len(processed_entries)}")
    print(f"Run-on entries detected: {runon_count}")
    print(f"Independent entries: {len(processed_entries) - runon_count}")


def main():
    parser = argparse.ArgumentParser(description="Process merged entries to detect run-ons")
    parser.add_argument("input_file", help="Input JSON file with merged entries")
    parser.add_argument("-o", "--output", default="processed_entries.json", 
                       help="Output JSON file (default: processed_entries.json)")
    parser.add_argument("--ip", default="localhost", help="VLLM server IP")
    parser.add_argument("--port", default=8000, type=int, help="VLLM server port") 
    parser.add_argument("--model-name", default="model", help="Model name")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        return 1
        
    process_runons(args.input_file, args.output, args.ip, args.port, args.model_name)
    return 0


if __name__ == "__main__":
    exit(main())