#!/usr/bin/env python3
"""
Simple test script to verify our PDF outline extractor functionality
"""

import os
import sys
import json
from parser import parse_pdf
from classifier import extract_title, classify_headings, build_outline

def test_functionality():
    """Test the PDF processing pipeline"""
    
    # Test with sample PDFs in input directory
    input_dir = "input"
    
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found!")
        return
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory!")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) for testing:")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    
    # Test with first PDF file
    test_file = pdf_files[0]
    pdf_path = os.path.join(input_dir, test_file)
    
    print(f"\n=== Testing with: {test_file} ===")
    
    try:
        # Step 1: Parse PDF
        print("1. Parsing PDF...")
        lines, doc_stats = parse_pdf(pdf_path)
        print(f"   ✓ Extracted {len(lines)} lines")
        print(f"   ✓ Document stats: {doc_stats}")
        
        # Step 2: Extract title
        print("2. Extracting title...")
        title, remaining_lines = extract_title(lines)
        print(f"   ✓ Title: '{title}'")
        print(f"   ✓ Remaining lines: {len(remaining_lines)}")
        
        # Step 3: Classify headings
        print("3. Classifying headings...")
        initial_headings = classify_headings(remaining_lines, doc_stats)
        print(f"   ✓ Found {len(initial_headings)} initial headings")
        
        # Step 4: Build final outline
        print("4. Building final outline...")
        final_headings = build_outline(initial_headings)
        print(f"   ✓ Final outline has {len(final_headings)} headings")
        
        # Step 5: Show results
        print("\n=== RESULTS ===")
        print(f"Title: {title}")
        print("Outline:")
        for i, heading in enumerate(final_headings, 1):
            print(f"  {i}. [{heading['level']}] {heading['text']} (Page {heading['page_num']})")
        
        # Step 6: Create JSON output
        output_dict = {
            "title": title,
            "outline": final_headings
        }
        
        # Save to test output file
        output_file = f"test_output_{test_file.replace('.pdf', '.json')}"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Test output saved to: {output_file}")
        print("✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_functionality()
