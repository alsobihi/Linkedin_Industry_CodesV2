import requests
from bs4 import BeautifulSoup
import csv # Import the csv module

def extract_and_join_tables(url):
    """
    Extracts all tables from a given URL, joins their data into a single list of rows,
    and adds a new column at the beginning of each row indicating the source table's name.

    Args:
        url (str): The URL of the webpage to extract tables from.

    Returns:
        list: A single list of lists, where each inner list represents a row
              from any of the extracted tables, with the first element being the
              name of the table it originated from.
              Returns an empty list if no tables are found or an error occurs.
    """
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

    # Find all table elements on the page
    tables = soup.find_all('table')
    if not tables:
        print("No tables found on the page.")
        return []

    all_combined_rows = []

    # Iterate through each table found
    for i, table in enumerate(tables):
        # Attempt to find a descriptive name for the table.
        # This tries to find the closest preceding heading (h1-h6) or a table caption.
        table_name = f"Table {i + 1}" # Default name if no specific title is found

        # 1. Look for the closest preceding heading tag (h1, h2, h3, h4, h5, h6)
        # This is a common pattern for tables that follow a section title.
        previous_heading = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if previous_heading and previous_heading.get_text(strip=True):
            table_name = previous_heading.get_text(strip=True)
        else:
            # 2. As a fallback, check for a <caption> tag within the table
            caption = table.find('caption')
            if caption and caption.get_text(strip=True):
                table_name = caption.get_text(strip=True)

        rows = table.find_all('tr')
        if not rows:
            # Skip empty tables
            continue

        # Extract cells (both headers 'th' and data 'td') from each row
        for row in rows:
            row_cells = []
            cells = row.find_all(['th', 'td'])
            for cell in cells:
                row_cells.append(cell.get_text(strip=True))

            # Prepend the identified table name to each row of data
            if row_cells: # Ensure the row actually contains data before adding
                all_combined_rows.append([table_name] + row_cells)

    return all_combined_rows

def write_to_csv(data, filename):
    """
    Writes a list of lists (table data) to a CSV file.

    Args:
        data (list): A list of lists, where each inner list is a row of data.
        filename (str): The name of the CSV file to create/write to.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in data:
                csv_writer.writerow(row)
        print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")

if __name__ == "__main__":
    target_url = "https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/industry-codes-v2"
    joined_tables = extract_and_join_tables(target_url)

    if joined_tables:
        print(f"Successfully extracted and joined tables from {target_url}\n")
        # Print the first few rows of the combined table to show the format
        print("--- Combined Table (first 10 rows) ---")
        for i, row in enumerate(joined_tables):
            if i < 10: # Displaying only the first 10 rows for brevity
                print(row)
            else:
                break
        print(f"\n... (and {len(joined_tables) - 10} more rows). Total {len(joined_tables)} rows extracted.")

        # --- New: Export to CSV ---
        output_csv_filename = "linkedin_industry_codes.csv"
        write_to_csv(joined_tables, output_csv_filename)
        # --- End New ---

    else:
        print("Failed to extract or join any tables, or no tables were found.")
