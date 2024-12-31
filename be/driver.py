
import secrets
import string
import models
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import (
        EquityDB, 
        EquityCreate, 
        EquityRepository
    )
    
#    from database import SessionLocal

def load_data_from_csv():
    import csv
    import pandas as pd
    nse_data = pd.read_csv('nse_data.csv')
    bse_data = pd.read_csv('bse_data.csv')
    
    #Strip leading and trailing spaces and tabs from all columns
    nse_data = nse_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    bse_data = bse_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # Strip leading and trailing spaces and tabs from all columns
    nse_data = nse_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    bse_data = bse_data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


    nse_data['From Exchange'] = 'NSE'
    bse_data['From Exchange'] = 'BSE'
    #filter
    bse_data  = bse_data[bse_data['Status'].isin(['Active', 'Suspended'])]
    # Remove rows where 'ISIN No' column is empty
    bse_data = bse_data.dropna(subset=['ISIN No'])
    nse_data = nse_data.dropna(subset=['ISIN No'])
    
    merged = pd.merge(bse_data, nse_data, how='outer', on='ISIN No')

    # Drop rows where a specific column has the value '-'
    merged = merged[merged['ISIN No'] != '-']  # boolean indexing
    

    #print(f"Merged Columns {merged.columns}")
    columns_to_convert = ['Security Code', 'Face Value']  # Replace with your column names
    for column in columns_to_convert:
        #merged[column] = merged[column].astype(int)
        merged[column] = pd.to_numeric(merged[column], errors='coerce').fillna(0).astype(int)
    merged.to_csv('merged.csv', index=False)
    
    to_db = merged[['ISIN No','Security Code', 'Security Id', 'Security Name','From Exchange_x', 'From Exchange_y','SYMBOL','NAME OF COMPANY',' DATE OF LISTING', ]]
    
    #print(f"Selected Columns {to_db.columns}")
    to_db = to_db.rename(columns={
        'Security Code': 'bse_security_code', 
        'Security Id': 'bse_security_id',
        'SYMBOL': 'nse_symbol',
        ' DATE OF LISTING': 'date_of_listing',
        'NAME OF COMPANY': 'name_of_company'
    })

    print(f"length of nse_data: {len(nse_data)}\nlength of bse_data: {len(bse_data)}\nlength of merged  : {len(merged)}")
    to_db.to_csv('to_db.csv', index=False)



engine = create_engine('postgresql://postgres:postgres@127.0.0.1:5432/equitydb')
#Base = declarative_base()
#Base.metadata.create_all(bind=engine)
#print(f"Base.metadata.tables: {models.Base.metadata.tables}")
models.Base.metadata.create_all(bind=engine)
#print(f"\n\n\n After create alll\n\n\n")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = Session()

def get_from_and_load_to_db():
    
    

    to_db = pd.read_csv('to_db.csv')
    to_db = to_db.where(pd.notnull(to_db), None)

    equity_objects = []
    for index, row in to_db.iterrows():
        
        to_db_bse_security_code = "NA"
        to_db_bse_security_id = "NA"
        to_db_nse_symbol = "NA"
        to_db_date_of_listing = "NA"
        to_db_name_of_company = "NA"
        to_db_nse_symbol = "NA"
        to_db_industry = "NA"
        to_db_sector = "NA"
        to_db_v_c_name = "NA"
        to_db_v_c_desc = "NA"
        
        #Defaults
        to_db_isin = row['ISIN No']
        
        #print(f"index: {index} row: {row}")
        if row['ISIN No'] == None:
            continue
        total_rows = len(to_db)
        for index, row in to_db.iterrows():
            if index % (total_rows // 10) == 0:
                progress = (index / total_rows) * 100
                print(f"Processing: {progress:.2f}% complete")

        length = secrets.randbelow(4) + 3
        safe_chars = (string.ascii_letters + string.digits).replace('l', '') \
            .replace('1', '').replace('I', '').replace('O', '').replace('0', '')
        rand_gen_str = ''.join(secrets.choice(safe_chars) for _ in range(length))
        #print (f" length: {length} string: {rand_gen_str}")

        if row['From Exchange_x'] == 'BSE' and row['From Exchange_y'] == 'NSE':
            #Equity is listed on both exchanges
            to_db_bse_security_code = str(row['bse_security_code'])
            to_db_bse_security_id = row['bse_security_id']
            to_db_name_of_company = row['name_of_company']
            to_db_nse_symbol = row['nse_symbol']
            to_db_date_of_listing = row['date_of_listing']
        elif row['From Exchange_x'] == 'BSE' and row['From Exchange_y'] == None:
            #Equity is listed only on BSE
            to_db_from_exchange = "BSE"
            to_db_bse_security_code = str(row['bse_security_code'])
            to_db_bse_security_id = row['bse_security_id']
            to_db_name_of_company = row['Security Name']
        elif row['From Exchange_x'] == None and row['From Exchange_y'] == 'NSE':
            #Equity is listed only on NSE
            to_db_from_exchange = "NSE" #default value
            to_db_nse_symbol = row['nse_symbol']
            to_db_name_of_company = row['name_of_company']
            to_db_date_of_listing = row['date_of_listing']
        
        #print(f" {type(to_db_isin)} to_db_isin: {to_db_isin}\n to_db_bse_security_code: {to_db_bse_security_code}\n to_db_bse_security_id: {to_db_bse_security_id}\n to_db_nse_symbol: {to_db_nse_symbol}\n to_db_date_of_listing: {to_db_date_of_listing}\n to_db_name_of_company: {to_db_name_of_company}\n to_db_nse_symbol: {to_db_nse_symbol}")

        to_db_v_c_name = f"{to_db_isin}_{rand_gen_str}"
        to_db_v_c_desc = f"Vector Collection for {to_db_name_of_company}"

        equity = EquityCreate(
            isin_no= to_db_isin,
            bse_security_code=to_db_bse_security_code,
            bse_security_id=to_db_bse_security_id,
            nse_symbol=to_db_nse_symbol,
            date_of_listing=to_db_date_of_listing,
            name_of_company=to_db_name_of_company,
            from_exchange=to_db_from_exchange,
            industry=to_db_industry,
            sector=to_db_sector,
            vector_collection_name=to_db_v_c_name,
            vector_collection_desc=to_db_v_c_desc,
            comments="NA"
        )
        equity_objects.append(equity)

    equity_repo = EquityRepository(db)

    for equity in equity_objects:
        equity_repo.create_Equity(equity)

    

def main():
    #load_data_from_csv()
    get_from_and_load_to_db()

if __name__ == '__main__':
    main()