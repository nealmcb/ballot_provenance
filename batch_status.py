from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET
import sys
import datetime

Base = declarative_base()

class BatchStatus(Base):
    __tablename__ = 'batch_status'
    # Defining composite primary key (Tabulator Number, Batch Number)
    tabulator_number = Column(Integer, primary_key=True)
    batch_number = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    tabulator_name = Column(String)
    result_file_name = Column(String)
    lead_ballots = Column(Integer)
    total_ballots = Column(Integer)
    result_state = Column(String)
    adjudication_state = Column(String)


def xml_to_batch_statuses(file_path):
    ns = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
    tree = ET.parse(file_path)
    root = tree.getroot()
    rows = root.findall('.//ss:Worksheet/ss:Table/ss:Row', ns)
    
    session = Session()
    for idx, row in enumerate(rows):
        cells = row.findall('ss:Cell/ss:Data', ns)

        # We check if the row has sufficient cells and skip if any cell content looks non-numeric where it shouldn't
        if len(cells) < 9 or not cells[1].text.isdigit() or not cells[3].text.isdigit():
            continue  # Skip header rows or any malformed rows

        datetime_str = cells[0].text
        tabulator_number = int(cells[1].text)
        tabulator_name = cells[2].text
        batch_number = int(cells[3].text)
        result_file_name = cells[4].text
        lead_ballots = int(cells[5].text)
        total_ballots = int(cells[6].text)
        result_state = cells[7].text
        adjudication_state = cells[8].text

        # Convert string datetime to datetime object
        datetime_obj = datetime.datetime.strptime(datetime_str, "%m/%d/%Y %I:%M:%S %p")

        # Check if exists
        existing = session.query(BatchStatus).filter_by(tabulator_number=tabulator_number, batch_number=batch_number).first()
        if existing:
            existing.datetime = datetime_obj
            existing.tabulator_name = tabulator_name
            existing.result_file_name = result_file_name
            existing.lead_ballots = lead_ballots
            existing.total_ballots = total_ballots
            existing.result_state = result_state
            existing.adjudication_state = adjudication_state
        else:
            new_record = BatchStatus(datetime=datetime_obj, tabulator_number=tabulator_number,
                                     tabulator_name=tabulator_name, batch_number=batch_number,
                                     result_file_name=result_file_name, lead_ballots=lead_ballots,
                                     total_ballots=total_ballots, result_state=result_state,
                                     adjudication_state=adjudication_state)
            session.add(new_record)
        session.commit()
    session.close()


engine = create_engine('sqlite:///election_provenance.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    xml_to_batch_statuses(file_path)
