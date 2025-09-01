dict_promptmode_to_prompt = {
    # prompt_layout_all_en: parse all layout info in json format.
    "prompt_layout_all_en": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - Formula: Format its text as LaTeX.
    - Table: Format its text as HTML.
    - All Others (Text, Title, etc.): Format their text as Markdown.

4. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.

5. Final Output: The entire output must be a single JSON object.
""",

    # prompt_layout_only_en: layout detection
    "prompt_layout_only_en": """Please output the layout information from this PDF image, including each layout's bbox and its category. The bbox should be in the format [x1, y1, x2, y2]. The layout categories for the PDF document include ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']. Do not output the corresponding text. The layout result should be in JSON format.""",

    # prompt_layout_only_en: parse ocr text except the Page-header and Page-footer
    "prompt_ocr": """Extract the text content from this image.""",

    # prompt_grounding_ocr: extract text content in the given bounding box
    "prompt_grounding_ocr": """Extract text from the given bounding box on the image (format: [x1, y1, x2, y2]).\nBounding Box:\n""",

    # "prompt_table_html": """Convert the table in this image to HTML.""",
    # "prompt_table_latex": """Convert the table in this image to LaTeX.""",
    # "prompt_formula_latex": """Convert the formula in this image to LaTeX.""",
    
    # prompt_layout_text_only: parse all layout info but format everything as plain text
    "prompt_layout_text_only": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Text', 'Title'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - All content (Text, Title, etc.): Format as plain text, preserving original spacing and line breaks as much as possible.
    - IMPORTANT: Do not classify content as 'Table'. Dictionary entries, glossaries, and similar structured text should be classified as 'Text' and formatted as plain text.

4. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.
    - Avoid HTML formatting - output all text content as plain text only.

5. Final Output: The entire output must be a single JSON object.""",

    # prompt_layout_text_only_no_tables: specifically for dictionary/glossary content
    "prompt_layout_text_only_no_tables": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Text'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - All content (Text, Title, etc.): Format as plain text, preserving original spacing and line breaks as much as possible.
    - CRITICAL: Dictionary entries, glossaries, word lists, and any structured text content should be classified as 'Text', not as tables or list items.
    - Do not use HTML formatting under any circumstances - all text must be plain text.

4. Special Instructions for Dictionary Content:
    - If you see dictionary entries with words and definitions, classify them as 'Text'
    - If you see glossaries or word lists, classify them as 'Text'
    - If you see any structured content that might look like a table or list, treat it as 'Text'
    - Preserve the original formatting and spacing of the text
    - IMPORTANT: Do not classify content as 'List-item'. Dictionary entries should be 'Text'.

5. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.
    - No HTML, no tables, no list items - only plain text output.

6. Final Output: The entire output must be a single JSON object.""",

    # prompt_dictionary_only: ultra-specific for dictionary content
    "prompt_dictionary_only": """You are processing a dictionary page. Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: ONLY use these categories: ['Page-footer', 'Page-header', 'Section-header', 'Text'].

3. Text Extraction & Formatting Rules:
    - All dictionary entries should be classified as 'Text'
    - All content should be formatted as plain text, preserving original spacing and line breaks
    - Do not use HTML formatting under any circumstances
    - Do not classify anything as 'List-item', 'Table', or any other category not listed above

4. Dictionary-Specific Instructions:
    - Dictionary entries with words and definitions = 'Text'
    - Glossaries or word lists = 'Text'
    - Any structured content = 'Text'
    - Only use 'Section-header' for letter headers (A, B, C, etc.)
    - Only use 'Page-header' and 'Page-footer' for actual page headers/footers

5. Constraints:
    - The output text must be the original text from the image, with no translation
    - All layout elements must be sorted according to human reading order
    - Only plain text output - no HTML, no tables, no list items

6. Final Output: The entire output must be a single JSON object.""",
}
