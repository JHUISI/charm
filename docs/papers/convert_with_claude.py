#!/usr/bin/env python3
"""
Convert PDF page images to markdown using Claude's vision capabilities.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python convert_with_claude.py <paper_name>
    
Example:
    python convert_with_claude.py Cramer_Damgard_Schoenmakers_1994
"""

import anthropic
import base64
import os
import sys
from pathlib import Path


def encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def convert_page_to_markdown(client: anthropic.Anthropic, image_path: str, page_num: int) -> str:
    """Convert a single page image to markdown using Claude."""
    print(f"  Processing page {page_num}...")
    
    image_data = encode_image(image_path)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Convert this academic paper page to markdown format.

IMPORTANT RULES:
1. Convert ALL mathematical equations to LaTeX format using $...$ for inline and $$...$$ for display equations
2. Preserve the document structure (headings, paragraphs, lists)
3. Use proper markdown formatting for emphasis, bold, etc.
4. For protocols/algorithms, use code blocks or structured formatting
5. Preserve all Greek letters, subscripts, superscripts accurately
6. If there are figures or diagrams, describe them in [Figure: description] format
7. Do NOT add any commentary - just output the converted markdown

Output ONLY the markdown content, nothing else."""
                    }
                ],
            }
        ],
    )
    
    return message.content[0].text


def convert_paper(paper_name: str):
    """Convert all pages of a paper to markdown."""
    images_dir = Path(f"images/{paper_name}")
    output_file = Path(f"{paper_name}_claude.md")
    
    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}")
        sys.exit(1)
    
    # Get all page images sorted
    page_images = sorted(images_dir.glob("page_*.png"))
    if not page_images:
        print(f"Error: No page images found in {images_dir}")
        sys.exit(1)
    
    print(f"Found {len(page_images)} pages for {paper_name}")
    
    # Initialize Anthropic client
    client = anthropic.Anthropic()
    
    # Convert each page
    all_markdown = []
    for i, image_path in enumerate(page_images, 1):
        try:
            md = convert_page_to_markdown(client, str(image_path), i)
            all_markdown.append(f"<!-- Page {i} -->\n\n{md}")
        except Exception as e:
            print(f"  Error on page {i}: {e}")
            all_markdown.append(f"<!-- Page {i} - ERROR: {e} -->\n\n")
    
    # Merge and save
    final_md = "\n\n---\n\n".join(all_markdown)
    
    with open(output_file, "w") as f:
        f.write(final_md)
    
    print(f"\nSaved to {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_with_claude.py <paper_name>")
        print("Example: python convert_with_claude.py Cramer_Damgard_Schoenmakers_1994")
        sys.exit(1)
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    convert_paper(sys.argv[1])

