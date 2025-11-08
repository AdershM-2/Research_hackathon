#!/usr/bin/env python3
"""
Convert markdown to PDF using markdown and reportlab
"""

import markdown
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from html.parser import HTMLParser
import re

class HTMLToReportLab(HTMLParser):
    """Parse HTML and convert to ReportLab flowables"""

    def __init__(self):
        super().__init__()
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.current_text = []
        self.in_list = False
        self.list_items = []
        self.table_data = []
        self.in_table = False
        self.current_row = []
        self.in_code_block = False
        self.code_block_text = []

    def _setup_styles(self):
        """Setup custom styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=30,
            borderWidth=0,
            borderPadding=5,
            borderColor=colors.HexColor('#3498db'),
        ))

        # Heading 2
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20,
        ))

        # Heading 3
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
        ))

        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=8,
            fontName='Courier',
            textColor=colors.HexColor('#c7254e'),
            backColor=colors.HexColor('#f4f4f4'),
            borderWidth=1,
            borderColor=colors.HexColor('#ddd'),
            borderPadding=5,
        ))

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_tag = 'h1'
        elif tag == 'h2':
            self.current_tag = 'h2'
        elif tag == 'h3':
            self.current_tag = 'h3'
        elif tag == 'p':
            self.current_tag = 'p'
        elif tag == 'code':
            self.current_tag = 'code'
        elif tag == 'pre':
            self.in_code_block = True
            self.code_block_text = []
        elif tag == 'ul' or tag == 'ol':
            self.in_list = True
            self.list_items = []
        elif tag == 'li':
            self.current_tag = 'li'
        elif tag == 'table':
            self.in_table = True
            self.table_data = []
        elif tag == 'tr':
            self.current_row = []
        elif tag in ['th', 'td']:
            self.current_tag = tag
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')

    def handle_endtag(self, tag):
        if tag == 'h1' and hasattr(self, 'current_tag'):
            text = ''.join(self.current_text)
            self.story.append(Paragraph(text, self.styles['CustomTitle']))
            self.story.append(Spacer(1, 0.2*inch))
            self.current_text = []
        elif tag == 'h2' and hasattr(self, 'current_tag'):
            text = ''.join(self.current_text)
            self.story.append(Paragraph(text, self.styles['CustomHeading2']))
            self.story.append(Spacer(1, 0.1*inch))
            self.current_text = []
        elif tag == 'h3' and hasattr(self, 'current_tag'):
            text = ''.join(self.current_text)
            self.story.append(Paragraph(text, self.styles['CustomHeading3']))
            self.current_text = []
        elif tag == 'p':
            text = ''.join(self.current_text)
            if text.strip():
                self.story.append(Paragraph(text, self.styles['Normal']))
                self.story.append(Spacer(1, 0.1*inch))
            self.current_text = []
        elif tag == 'pre':
            if self.in_code_block:
                code_text = '\n'.join(self.code_block_text)
                # Clean up code text
                code_text = code_text.replace('<code>', '').replace('</code>', '')
                pre = Preformatted(code_text, self.styles['CustomCode'])
                self.story.append(pre)
                self.story.append(Spacer(1, 0.1*inch))
                self.in_code_block = False
                self.code_block_text = []
        elif tag in ['ul', 'ol']:
            self.in_list = False
            for item in self.list_items:
                self.story.append(Paragraph(f"• {item}", self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*inch))
            self.list_items = []
        elif tag == 'li':
            text = ''.join(self.current_text)
            self.list_items.append(text)
            self.current_text = []
        elif tag == 'table':
            if self.table_data:
                t = Table(self.table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                self.story.append(t)
                self.story.append(Spacer(1, 0.2*inch))
            self.in_table = False
            self.table_data = []
        elif tag == 'tr':
            if self.current_row:
                self.table_data.append(self.current_row)
            self.current_row = []
        elif tag in ['th', 'td']:
            text = ''.join(self.current_text)
            self.current_row.append(text)
            self.current_text = []
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('</b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('</i>')

    def handle_data(self, data):
        if self.in_code_block:
            self.code_block_text.append(data)
        else:
            self.current_text.append(data)

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF using reportlab"""

    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code']
    )

    # Parse HTML
    parser = HTMLToReportLab()
    parser.feed(html_content)

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    doc.build(parser.story)
    print(f"[OK] PDF created successfully: {pdf_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        md_file = sys.argv[1]
        pdf_file = sys.argv[2]
    else:
        md_file = "BACKGROUND_TUTORIAL.md"
        pdf_file = "BACKGROUND_TUTORIAL.pdf"
    markdown_to_pdf(md_file, pdf_file)
