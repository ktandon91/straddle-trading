import os
import pandas as pd
import glob
from sqlalchemy import create_engine
import psycopg2
import io
from datetime import datetime

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/trading')
columns = ['ticker', 'date', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_interest']

BASE_DIR = 'GDFL2016-2020'

def format_date(value):
    formatted_value = datetime.strptime(value,"%d/%m/%Y")
    return formatted_value

def format_time(value):
    formatted_value = datetime.strptime(value.strip(),"%H:%M:%S")
    return formatted_value


for root, dirs, files in os.walk("."):
    for file in files:
        if 'GFDLNFO' in file:
            FILE = os.path.join(root,file)
            print(FILE)
            df = pd.read_csv(FILE)
            df.columns = columns
            df.fillna(" ")
            df['date'] = df['date'].apply(format_date)
            df['time'] = df['time'].apply(format_time)
            df['volume']=df['volume'].astype('int64')
            df['open_interest']=df['open_interest'].astype('int64')
            # sql_query = df.head(0).to_sql('table_name', engine, if_exists='replace', index=False) #truncates the table
            conn = engine.raw_connection()
            cur = conn.cursor()
            output = io.StringIO()
            df.to_csv(output, sep='\t', header=False, index=False)
            output.seek(0)
            contents = output.getvalue()
            try:
                cur.copy_from(output, 'options_data', null="")  # null values become ''
            except psycopg2.errors.UniqueViolation as e:
                print(e)
                pass
            conn.commit()
            output.close()
