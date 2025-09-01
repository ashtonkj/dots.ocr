#!/usr/bin/env python3
"""
Test script to compare the old and new prompts for dictionary content.
This helps demonstrate how the new prompt should prevent table detection.
"""

import sys
sys.path.append('.')

from dots_ocr.utils.prompts import dict_promptmode_to_prompt


def compare_prompts():
    """Compare the old and new prompts for dictionary content."""
    print("Prompt Comparison for Dictionary Content")
    print("=" * 50)
    
    # Get the old prompt
    old_prompt = dict_promptmode_to_prompt.get("prompt_layout_text_only", "Not found")
    
    # Get the new prompt
    new_prompt = dict_promptmode_to_prompt.get("prompt_layout_text_only_no_tables", "Not found")
    
    print("\n1. OLD PROMPT (prompt_layout_text_only):")
    print("-" * 30)
    print(old_prompt)
    
    print("\n\n2. NEW PROMPT (prompt_layout_text_only_no_tables):")
    print("-" * 40)
    print(new_prompt)
    
    print("\n\n3. KEY DIFFERENCES:")
    print("-" * 20)
    
    # Analyze differences
    differences = [
        ("Categories", 
         "Old: Includes 'Table' in categories",
         "New: Removes 'Table' from categories"),
        ("Table Instructions",
         "Old: 'Table: Format their text as plain text...'",
         "New: No table instructions - tables not allowed"),
        ("Dictionary Instructions",
         "Old: No specific dictionary instructions",
         "New: Explicit instructions to classify dictionary content as 'Text'"),
        ("HTML Formatting",
         "Old: Mentions HTML but tries to avoid it",
         "New: 'Do not use HTML formatting under any circumstances'"),
        ("Special Instructions",
         "Old: General text formatting rules",
         "New: Specific instructions for dictionary entries, glossaries, word lists")
    ]
    
    for i, (category, old_desc, new_desc) in enumerate(differences, 1):
        print(f"\n{i}. {category}:")
        print(f"   ❌ {old_desc}")
        print(f"   ✅ {new_desc}")
    
    print("\n\n4. EXPECTED BEHAVIOR WITH NEW PROMPT:")
    print("-" * 35)
    expected_behavior = [
        "Dictionary entries will be classified as 'Text' instead of 'Table'",
        "No HTML formatting in the output",
        "All content will be plain text",
        "Original spacing and formatting will be preserved",
        "No table detection for structured text content"
    ]
    
    for i, behavior in enumerate(expected_behavior, 1):
        print(f"   {i}. {behavior}")
    
    print("\n\n5. USAGE:")
    print("-" * 8)
    print("The enhanced parser now uses the new prompt by default:")
    print("   ./parse_pdf_enhanced.sh document.pdf output/")
    print("\nOr explicitly specify the new prompt:")
    print("   ./parse_pdf_enhanced.sh document.pdf output/ --prompt-mode prompt_layout_text_only_no_tables")
    print("\nTo use the old prompt (if needed):")
    print("   ./parse_pdf_enhanced.sh document.pdf output/ --prompt-mode prompt_layout_text_only")


def main():
    """Run the prompt comparison."""
    try:
        compare_prompts()
        print("\n" + "=" * 50)
        print("✅ Prompt comparison completed!")
        print("The new prompt should significantly reduce table detection for dictionary content.")
        
    except Exception as e:
        print(f"Error comparing prompts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

