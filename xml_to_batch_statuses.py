import xml.etree.ElementTree as ET
import sys

def xml_to_batch_statuses(file_path):
    # Define namespaces to simplify querying with ElementTree
    ns = {
        'ss': 'urn:schemas-microsoft-com:office:spreadsheet'
    }

    # Load and parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iterate through the rows in the XML file, skipping the header row
    rows = root.findall('.//ss:Worksheet/ss:Table/ss:Row', ns)
    header = True  # Assuming first row with data is a header
    for row in rows:
        if header:
            header = False  # Skip the first data row (header)
            continue

        # Initialize a dictionary to store batch details
        batch_info = {}
        cells = row.findall('ss:Cell/ss:Data', ns)

        if len(cells) == 9:  # Check if the row contains the expected number of cells
            batch_info['DateTime'] = cells[0].text
            batch_info['Tabulator Number'] = cells[1].text
            batch_info['Tabulator Name'] = cells[2].text
            batch_info['Batch Number'] = cells[3].text
            batch_info['Result File Name'] = cells[4].text
            batch_info['Lead Ballots'] = cells[5].text
            batch_info['Total Ballots'] = cells[6].text
            batch_info['Result State'] = cells[7].text
            batch_info['Adjudication State'] = cells[8].text
            yield batch_info

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    for batch_status in xml_to_batch_statuses(file_path):
        print(batch_status)
