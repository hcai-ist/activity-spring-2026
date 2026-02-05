#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
# ]
# ///
"""
Extract tables from Penn State budget allocation page and convert to markdown
"""

import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    """Fetch the webpage content"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_tables_to_markdown(html_content):
    """Extract all tables from HTML and convert to markdown format with fixed-width columns"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    markdown_output = []
    markdown_output.append("## Budget Allocations for Fiscal Years 2027 and 2028\n")
    
    # Find all tables on the page
    tables = soup.find_all('table')
    
    # Section titles mapping (in order they appear)
    section_titles = [
        "### UP Colleges",
        "### Commonwealth Campuses",
        "### Student Support Costs",
        "### Penn State IT",
        "### Physical Plant",
        "### Admin Support Costs"
    ]
    
    for idx, table in enumerate(tables):
        # Add section title
        if idx < len(section_titles):
            markdown_output.append(f"\n{section_titles[idx]}\n")
        
        # Extract all rows first to calculate column widths
        rows = table.find_all('tr')
        table_data = []
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            table_data.append(cell_texts)
        
        # Calculate maximum width for each column
        if not table_data:
            continue
            
        num_columns = len(table_data[0])
        col_widths = [0] * num_columns
        
        for row in table_data:
            for col_idx, cell in enumerate(row):
                col_widths[col_idx] = max(col_widths[col_idx], len(cell))
        
        # Create formatted rows
        for row_idx, row in enumerate(table_data):
            # Pad each cell to its column width
            padded_cells = []
            for col_idx, cell in enumerate(row):
                # Right-align numbers (columns with budget/change data), left-align text
                if col_idx > 0 and any(c.isdigit() for c in cell):
                    padded_cells.append(cell.rjust(col_widths[col_idx]))
                else:
                    padded_cells.append(cell.ljust(col_widths[col_idx]))
            
            # Create markdown table row with proper spacing
            markdown_row = "| " + " | ".join(padded_cells) + " |"
            markdown_output.append(markdown_row)
            
            # Add separator after header row
            if row_idx == 0:
                separators = []
                for col_idx, width in enumerate(col_widths):
                    # Right-align separator for numeric columns
                    if col_idx > 0:
                        separators.append("-" * width + ":")
                    else:
                        separators.append("-" * (width + 1))
                separator = "| " + " | ".join(separators) + " |"
                markdown_output.append(separator)
        
        markdown_output.append("")  # Empty line between tables
    
    # Add note at the end
    markdown_output.append("\n*Note: Allocations do not include grad assistant grant-in-aid*")
    
    return "\n".join(markdown_output)


def main():
    url = "https://budgetandfinance.psu.edu/budget-allocations"
    
    print("Fetching webpage...")
    html_content = fetch_page(url)
    
    print("Extracting tables and converting to markdown...")
    markdown_tables = extract_tables_to_markdown(html_content)
    
    # Save to file
    output_file = "budget_tables.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_tables)
    
    print(f"\nMarkdown tables saved to: {output_file}")
    print("\n" + "="*60)
    print("Preview:")
    print("="*60)
    print(markdown_tables[:1000] + "...\n")


if __name__ == "__main__":
    main()
