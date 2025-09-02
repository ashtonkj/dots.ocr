#!/usr/bin/env python3

import json
import os
import argparse
import re
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


def has_valid_entry_format(text):
    """
    Check if text starts with a valid dictionary entry format using regex
    """
    # Pattern 1: Chinese characters followed by (rad.XX) and romanization
    # Example: 挨 (rad.64) āi
    pattern1 = r'^[\u4e00-\u9fff]+(?:\s*\[[\u4e00-\u9fff\s]+\])?\s*\(rad\.\d+\)\s+[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùüńňǹ]+'
    
    # Pattern 2: Romanization (one or more words) followed by Chinese characters  
    # Example: āi shēn pào 挨身炮, àn ná fǎ 按拿法
    pattern2 = r'^[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùüńňǹ]+(?:\s+[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùüńňǹ]+)*\s+[\u4e00-\u9fff]+'
    
    # Pattern 3: Just Chinese characters followed by romanization (for simple entries)
    # Example: 矮 (rad.111) ǎi
    pattern3 = r'^[\u4e00-\u9fff]+\s+[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùüńňǹ]+'
    
    return bool(re.match(pattern1, text) or re.match(pattern2, text) or re.match(pattern3, text))


def is_runon_entry(current_entry, previous_entry):
    """
    Determine if current entry is a run-on using regex first, then LLM as backup
    """
    # First check with regex - if it has valid format, it's likely not a run-on
    if has_valid_entry_format(current_entry):
        return False
    
    # If regex suggests it might be a run-on, ask LLM for confirmation
    prompt = f"""Is this text a continuation/run-on of the previous dictionary entry?

Previous: "{previous_entry}"
Current: "{current_entry}"

The current text does NOT start with the standard dictionary format (Chinese + romanization OR romanization + Chinese).
Is it continuing the definition from the previous entry? Answer YES or NO."""

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
        
        # Use regex + LLM to determine if this is a run-on
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