import os
import json
from parser import parse_pdf
from classifier import extract_title, classify_headings, build_outline


def main():
    """
    Local test version of main orchestration script.
    Uses local input/output directories instead of Docker paths.
    """
    # Define input and output directory paths (local versions)
    input_dir = "input"
    output_dir = "output"
    
    # Check if output directory exists, create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of all files in input directory
    input_files = os.listdir(input_dir)
    
    # Loop through each filename
    for filename in input_files:
        # Check if file is a PDF
        if filename.endswith('.pdf'):
            # Construct full input and output file paths
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)
            
            # Print processing message
            print(f"Processing file: {filename}")
            
            try:
                # Parse PDF to get lines and document stats
                lines, doc_stats = parse_pdf(input_path)
                
                # Extract title and get remaining lines
                title, remaining_lines = extract_title(lines, doc_stats)
                
                # Classify headings to get initial list
                initial_headings = classify_headings(remaining_lines, doc_stats)
                
                # Build final validated outline
                final_headings = build_outline(initial_headings)
                
                # Construct final output dictionary in required format
                output_dict = {
                    "title": title,
                    "outline": final_headings
                }
                
                # Write dictionary to JSON file with proper formatting
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    json.dump(output_dict, output_file, indent=2, ensure_ascii=False)
                
                # Print success message
                print(f"Successfully processed: {filename} -> {output_filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


if __name__ == '__main__':
    main()
