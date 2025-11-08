#!/usr/bin/env python3
"""
Convert markdown files to PDF using markdown2 and weasyprint
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import sys

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )

    # Create full HTML document with CSS styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-right {{
                    content: counter(page) " / " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }}
            }}

            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 10pt;
            }}

            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
                font-size: 24pt;
                page-break-before: always;
            }}

            h1:first-of-type {{
                page-break-before: avoid;
            }}

            h2 {{
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 5px;
                margin-top: 25px;
                font-size: 18pt;
            }}

            h3 {{
                color: #34495e;
                margin-top: 20px;
                font-size: 14pt;
            }}

            h4 {{
                color: #555;
                margin-top: 15px;
                font-size: 12pt;
            }}

            code {{
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                color: #c7254e;
            }}

            pre {{
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-left: 4px solid #3498db;
                padding: 10px;
                overflow-x: auto;
                border-radius: 4px;
                page-break-inside: avoid;
            }}

            pre code {{
                background-color: transparent;
                padding: 0;
                color: #333;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
                page-break-inside: avoid;
                font-size: 9pt;
            }}

            th {{
                background-color: #3498db;
                color: white;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }}

            td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}

            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-left: 0;
                color: #555;
                font-style: italic;
            }}

            ul, ol {{
                margin-left: 20px;
            }}

            li {{
                margin: 5px 0;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            hr {{
                border: none;
                border-top: 2px solid #ddd;
                margin: 20px 0;
            }}

            .page-break {{
                page-break-after: always;
            }}

            strong {{
                color: #2c3e50;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Create PDF
    font_config = FontConfiguration()
    html = HTML(string=full_html)
    html.write_pdf(pdf_file, font_config=font_config)

    print(f"✓ PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        md_file = sys.argv[1]
        pdf_file = sys.argv[2]
    else:
        md_file = "BACKGROUND_TUTORIAL.md"
        pdf_file = "BACKGROUND_TUTORIAL.pdf"

    markdown_to_pdf(md_file, pdf_file)
