import fitz
import os
import re
from collections import Counter


def get_doc_stats(doc):
    """
    Iterate through the entire document to find the most common font size and font family,
    which will represent the document's body text style.
    """
    font_sizes = []
    font_names = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_dict = page.get_text('dict')
        
        for block in text_dict['blocks']:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        if span['text'].strip():  # Only count non-empty text
                            font_sizes.append(round(span['size']))
                            font_names.append(span['font'])
    
    # Find most common font size and font name
    size_counter = Counter(font_sizes)
    font_counter = Counter(font_names)
    
    most_common_size = size_counter.most_common(1)[0][0] if size_counter else 12
    most_common_font = font_counter.most_common(1)[0][0] if font_counter else ""
    
    return {
        'most_common_size': most_common_size,
        'most_common_font': most_common_font
    }


def parse_pdf(pdf_path):
    """
    Parse a PDF file and extract detailed information about every line of text,
    calculating a rich set of features for each line.
    """
    doc = fitz.open(pdf_path)
    doc_stats = get_doc_stats(doc)
    
    lines = []
    previous_line_bottom = 0
    
    for page_num, page in enumerate(doc):
        page_width = page.rect.width
        page_center = page_width / 2
        
        # Reset vertical spacing for each new page
        if page_num > 0:
            previous_line_bottom = 0

        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]
        
        for block in blocks:
            for line in block.get("lines", []):
                text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                if not text or not line.get("spans"):
                    continue

                # --- Line Properties ---
                first_span = line["spans"][0]
                font_size = first_span["size"]
                font_name = first_span["font"]
                x0, y0, x1, y1 = line["bbox"]
                
                # --- Feature Calculation ---
                is_bold = any(kw in font_name.lower() for kw in ['bold', 'black', 'heavy', 'semb'])
                is_italic = any(kw in font_name.lower() for kw in ['italic', 'oblique'])
                line_center = (x0 + x1) / 2
                is_centered = abs(line_center - page_center) < 10
                
                # Calculate vertical space considering page breaks
                vertical_space_before = y0 - previous_line_bottom if previous_line_bottom != 0 else 20

                alpha_chars = sum(1 for c in text if c.isalpha())
                is_all_caps = text.isupper() and alpha_chars >= 2
                
                # Calculate numeric level (e.g., 1. -> 1, 1.1. -> 2)
                numeric_match = re.match(r'^(\d+(\.\d+)*)\.?\s', text)
                numeric_level = numeric_match.group(1).count('.') + 1 if numeric_match else 0
                
                ends_with_punctuation = text.rstrip() and text.rstrip()[-1] in '.!?'
                word_count = len(text.split())

                # --- Create Line Dictionary ---
                line_dict = {
                    'text': text,
                    'font_size': font_size,
                    'font_name': font_name,
                    'is_bold': is_bold,
                    'is_italic': is_italic,
                    'is_centered': is_centered,
                    'indentation': x0,
                    'vertical_space_before': vertical_space_before,
                    'line_length': len(text),
                    'word_count': word_count,
                    'is_all_caps': is_all_caps,
                    'numeric_level': numeric_level,
                    'ends_with_punctuation': ends_with_punctuation,
                    'page_num': page_num + 1,
                    'bbox': (x0, y0, x1, y1)
                }
                
                lines.append(line_dict)
                previous_line_bottom = y1

    doc.close()
    return lines, doc_stats