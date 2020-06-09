import psycopg2
import pandas as pd


class Connection:
    def __enter__(self):
        self._conn = psycopg2.connect("dbname=trading user=postgres password=postgres")
        self._curr = self._conn.cursor()
        return self._curr

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()



class OptionsDataFrameFromQuery:

    def __init__(self, query):
        self._query = query
        self._df = pd.DataFrame()

    def return_data_frame(self):
        with Connection() as curr:
            curr.execute(self._query)
            self._df = pd.DataFrame(curr.fetchall())
            colnames = [desc[0] for desc in curr.description]
            self._df.columns = colnames

        return self._df


# from queries.queries import dummy_query
# df = OptionsDataFrameFromQuery(query=dummy_query).return_data_frame()
# print(df.head())
