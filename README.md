# Adobe Hackathon: High-Accuracy Document Outline Extractor

## Approach

This solution implements a **Multi-Feature Heuristic Scoring Model** to extract structured outlines from PDF documents. This approach avoids the constraints of large ML models and relies on analyzing typographic and positional cues within the PDF to identify titles and heading hierarchies.

The system analyzes each line of text in the document and calculates a comprehensive "heading score" based on multiple features:

### Key Features Used for Scoring:

- **Font Size**: Larger fonts relative to the document's body text receive higher scores
- **Font Weight**: Bold fonts (inferred from font name keywords like 'bold', 'black', 'heavy', 'semibold') are prioritized
- **Vertical Spacing**: Lines with more white space above them are more likely to be headings
- **Text Content Patterns**: 
  - Numeric prefixes (1., 1.1., 1.1.2, etc.) strongly indicate structured headings
  - All-caps text formatting suggests emphasis
- **Positional Information**: 
  - Centered text alignment often indicates titles or major headings
  - Indentation patterns help establish hierarchy levels

The model then groups candidate headings by font size to establish a logical hierarchy (H1, H2, H3) and applies validation rules to ensure consistent document structure.

## Libraries Used

**PyMuPDF (fitz)** - The primary library chosen for this solution due to its:
- High performance PDF parsing capabilities
- Detailed feature extraction including font properties, positioning, and text formatting
- Ability to extract precise typographic information needed for heuristic analysis
- Lightweight footprint suitable for containerized deployment

## How to Build and Run

### Build Command:
```bash
docker build --platform linux/amd64 -t outline-extractor .
```

### Run Command:
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none outline-extractor
```

### Usage:
1. Place your PDF files in the `input/` directory
2. Run the Docker container using the command above
3. The container will automatically process all PDFs in the input folder
4. Corresponding JSON outline files will be generated in the `output/` folder
5. Each JSON file contains the extracted title and hierarchical outline structure

The solution runs completely offline with no network access required, making it suitable for secure document processing environments.
