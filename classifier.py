import re
from collections import defaultdict

def extract_title(lines, doc_stats):
    """
    Extracts the document title by finding the most prominent text on the first page.
    Returns the title and the remaining lines.
    """
    first_page_lines = [line for line in lines if line['page_num'] == 1]
    if not first_page_lines:
        return "", lines

    # Find the largest font size on the first page
    max_font_size = max(line['font_size'] for line in first_page_lines)
    
    # Title candidates are lines with large fonts, near the top, and likely centered
    candidates = [
        line for line in first_page_lines
        if line['font_size'] >= max_font_size - 2 and line['bbox'][1] < 400
    ]
    
    if not candidates:
        # Fallback for documents with no clear large title
        if first_page_lines:
            # Sort by vertical position and take the first few lines
            first_page_lines.sort(key=lambda x: x['bbox'][1])
            title_text = " ".join(line['text'] for line in first_page_lines[:2])
            title_lines_text = {line['text'] for line in first_page_lines[:2]}
            remaining_lines = [line for line in lines if line['text'] not in title_lines_text]
            return title_text.strip(), remaining_lines
        return "", lines

    # Sort candidates by font size (desc), then vertical position (asc)
    candidates.sort(key=lambda x: (-x['font_size'], x['bbox'][1]))
    
    title_lines = [candidates[0]] # Start with the most prominent line
    title_lines_text = {candidates[0]['text']}
    
    # Add subsequent lines if they are close vertically and seem to be part of the same title block
    last_y1 = candidates[0]['bbox'][3]
    for line in candidates[1:]:
        if (line['bbox'][1] - last_y1) < 20: # If vertical gap is small
            title_lines.append(line)
            title_lines_text.add(line['text'])
            last_y1 = line['bbox'][3]
        else:
            break

    title_text = " ".join(line['text'] for line in title_lines)
    remaining_lines = [line for line in lines if line['text'] not in title_lines_text]
    
    return title_text.strip(), remaining_lines


def score_line(line, doc_stats):
    """
    Calculates a 'heading score' for a line based on its features.
    """
    score = 0
    font_size_diff = line['font_size'] - doc_stats['most_common_size']
    
    if font_size_diff > 1:
        score += font_size_diff * 4

    if line['is_bold']: score += 15
    if line['is_all_caps']: score += 10
    # if line['numeric_level'] > 0: score += 25
    if line['vertical_space_before'] > 10: score += min(line['vertical_space_before'], 20)
    if line['is_centered']: score += 5
    if line['word_count'] < 10: score += 5
    if line['ends_with_punctuation']: score -= 15 # Penalize lines ending in punctuation
    
    # Penalize long lines
    score -= line['line_length'] * 0.05
    
    return score


def classify_headings(lines, doc_stats):
    """
    Identifies headings from a list of lines and assigns hierarchy levels.
    """
    candidates = []
    for line in lines:
        score = score_line(line, doc_stats)
        if score > 20:
            line['score'] = score
            candidates.append(line)

    if not candidates:
        return []

    # --- Identify Heading Styles ---
    # Group candidates by style (font size, bold, all caps)
    style_groups = defaultdict(list)
    for cand in candidates:
        # Do not use numeric headings to define styles
        # if cand['numeric_level'] > 0:
        #     continue
        style_key = (round(cand['font_size']), cand['is_bold'], cand['is_all_caps'])
        style_groups[style_key].append(cand)

    # Rank styles by prominence (font size, then avg score)
    ranked_styles = sorted(
        style_groups.keys(),
        key=lambda s: (-s[0], -sum(c['score'] for c in style_groups[s])/len(style_groups[s]))
    )
    
    style_to_level = {style: f"H{i+1}" for i, style in enumerate(ranked_styles) if i < 4}

    # --- Assign Levels to Headings ---
    headings = []
    for cand in candidates:
        # if cand['numeric_level'] > 0:
        #     level = f"H{cand['numeric_level']}"
        # else:
        style_key = (round(cand['font_size']), cand['is_bold'], cand['is_all_caps'])
        level = style_to_level.get(style_key, None)
        
        if level:
            headings.append({
                'level': level,
                'text': cand['text'].strip(),
                'page': cand['page_num'] - 1, # 0-indexed page
                'bbox_y': cand['bbox'][1] # For sorting
            })
            
    # Sort headings by their position in the document
    headings.sort(key=lambda x: (x['page'], x['bbox_y']))

    # Remove temporary sort key
    for h in headings:
        del h['bbox_y']
        
    return headings


def build_outline(headings):
    """
    Validates and corrects the heading hierarchy to ensure logical order.
    """
    if not headings:
        return []

    outline = []
    last_levels = [0, 0, 0, 0]  # Track last seen H1-H4

    for heading in headings:
        level_str = heading['level']
        level_num = int(level_str[1])

        # Promote if the first heading is not H1
        if not outline and level_num > 1:
            level_num = 1

        # Correct illogical skips (e.g., H1 -> H3 becomes H1 -> H2)
        if level_num > 1:
            if last_levels[level_num - 2] == 0:
                level_num = max(i + 1 for i, l in enumerate(last_levels) if l > 0) + 1
                level_num = min(level_num, 4) # Cap at H4

        heading['level'] = f'H{level_num}'

        # Update last seen levels
        last_levels[level_num - 1] = 1
        # Reset deeper levels
        for i in range(level_num, 4):
            last_levels[i] = 0

        outline.append(heading)

    return outline