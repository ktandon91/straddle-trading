from queries.queries import select_basis_ticker_and_date, \
    index_value_at_entry_time, nearest_expiry
from params import Params
from helpers import OptionsDataFrameFromQuery, Connection


class TimeStrategy:

    def __init__(self, params, query):
        self.params = params
        date = params.date.strftime('%Y-%m-%d')
        time = params.entry_time.strftime('%H:%M')
        self.ticker_value_query = index_value_at_entry_time \
            .format(date=date,time=time)
        self.ticker_names = self.get_ticker_name(self.ticker_value_query)
        ticker_names = tuple([str(ticker) for ticker in self.ticker_names])
        # ticker_names = ','.join(ticker_names)
        self.query = query.format(date=date, ticker_names=ticker_names)
        self.df = OptionsDataFrameFromQuery(query=self.query).return_data_frame()

        ##Tracking info for excel
        self.entry_price_ce = 0
        self.entry_price_pe = 0
        self.sl_ce = 0
        self.sl_pe = 0
        self.ce_exit_value = 0
        self.pe_exit_value = 0
        self.pe_exit_time = ""
        self.ce_exit_time = ""

    def get_ticker_name(self, query):
        temp = "BANKNIFTY"
        with Connection() as cursor:
            cursor.execute(query)
            try:
                result = cursor.fetchone()[0]
                actual_number = round(result / 100) * 100
            except Exception as e:
                print("{} for given entry no value found".format(e))
                raise Exception("Can't find value maybe data is not present for index")
            try:
                cursor.execute(nearest_expiry.format(date=self.params.date.strftime('%Y-%m-%d')))
                expiry_date_string = cursor.fetchone()[0]
                temp = temp + expiry_date_string + str(actual_number)
            except Exception as e:
                print("{} NEAREST EXPIRY ERROR".format(e))
                raise Exception("Can't find nearest date")

        return temp+"CE.NFO", temp+"PE.NFO"

    def strategy(self):
        df = self.df
        self.entry_price_ce = df[(df['ticker'] == self.ticker_names[0]) & (df['time'] == self.params.entry_time)]['open'].values[0]
        self.entry_price_pe = df[(df['ticker'] == self.ticker_names[1]) & (df['time'] == self.params.entry_time)]['open'].values[0]

        self.sl_ce = self.entry_price_ce + (self.entry_price_ce * self.params.stop_loss)
        self.sl_pe = self.entry_price_pe + (self.entry_price_pe * self.params.stop_loss)
        # print("PE entered at : {}, with SL {}".format(self.entry_price_pe, sl_pe))
        # print("CE entered at : {}, with SL {}".format(entry_price_ce, sl_ce))

        df_temp = df[(df['time'] > self.params.entry_time) & (df['time'])]

        row_ce_sl = \
            df_temp[(df_temp['ticker']==self.ticker_names[0])&((df_temp['open'] > self.sl_ce) | (df_temp['high']> self.sl_ce))]

        row_pe_sl =\
            df_temp[
            (df_temp['ticker'] == self.ticker_names[1]) & ((df_temp['open'] > self.sl_pe) | (df_temp['high'] > self.sl_pe))]

        if not row_ce_sl.empty:
            # print("CE SL HIT")
            if (row_ce_sl.iloc[0]['open'] > self.sl_ce):
                self.ce_exit_value = row_ce_sl.iloc[0]['open']
                # print("SL HIT VALUE {}".format(pe_exit_value))
            elif (row_ce_sl.iloc[0]['high'] > self.sl_ce):
                self.ce_exit_value = row_ce_sl.iloc[0]['high']
                # print("SL HIT VALUE {}".format(row_pe_sl.iloc[0]['high']))
            self.ce_exit_time = row_ce_sl.iloc[0]['time']
        else:
            # print("CE SL NOT HIT")
            self.ce_exit_value = df_temp[(df_temp['ticker'] == self.ticker_names[0]) & (df_temp['time'] > self.params.exit_time)].iloc[0]['open']
            self.ce_exit_time = df_temp[(df_temp['ticker'] == self.ticker_names[0]) & (df_temp['time'] > self.params.exit_time)].iloc[0]['time']
            # print(self.ce_exit_value)

        if not row_pe_sl.empty:
            # print("PE SL HIT")
            if(row_pe_sl.iloc[0]['open'] > self.sl_pe):
               self.pe_exit_value = row_pe_sl.iloc[0]['open']
                # print("SL HIT VALUE {}".format(pe_exit_value))
            elif (row_pe_sl.iloc[0]['high'] > self.sl_pe):
                self.pe_exit_value = row_pe_sl.iloc[0]['high']
                # print("SL HIT VALUE {}".format(row_pe_sl.iloc[0]['high']))
            self.pe_exit_time = row_pe_sl.iloc[0]['time']
            # print("SL HIT AT TIME {}".format(row_pe_sl.iloc[0]['time']))
        else:
            self.pe_exit_value = df_temp[(df_temp['ticker'] == self.ticker_names[1])
                                    & (df_temp['time'] > self.params.exit_time)].iloc[0]['open']
            self.pe_exit_time = df_temp[(df_temp['ticker'] == self.ticker_names[1])
                                    & (df_temp['time'] > self.params.exit_time)].iloc[0]['time']
            # print(pe_exit_value)
        # print("OVER HERE")


    def copy_to_file(self):
        # print("date : {}".format(self.params.date.strftime("%d/%m/%Y")))
        # print("entry price ce : {}".format(self.entry_price_ce))
        # print("entry price pe : {}".format(self.entry_price_pe))
        # print("sl ce : {}".format(self.sl_ce))
        # print("sl pe : {}".format(self.sl_pe))
        # print("ce_exit_value : {}".format(self.ce_exit_value))
        # print("pe_exit_value : {}".format(self.pe_exit_value))
        # print("ce_exit_time : {}".format(self.ce_exit_time))
        # print("pe_exit_time : {}".format(self.pe_exit_time))
        string_to_write = str(self.params.date.strftime("%d/%m/%Y"))+ "," + str(self.entry_price_ce) \
                          + "," + str(self.entry_price_pe) + "," + str(self.sl_ce) + "," + str(self.sl_pe) \
                          + "," + str(self.ce_exit_value) + "," + str(self.ce_exit_time) \
                          + "," + str(self.pe_exit_value) + "," + str(self.pe_exit_time)
        print(string_to_write)
        with open("results2.csv", "a") as filehandler:
            filehandler.write(string_to_write.strip())
            filehandler.write("\n")




query = select_basis_ticker_and_date

from datetime import timedelta, date

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


start_dt = date(2016, 6, 1)
end_dt = date(2018, 12, 31)

for date in daterange(start_dt, end_dt):
    date = date.strftime("%d/%m/%Y")
    print(date)
    try:
        params = Params(date=date, entry_time="10:25:59", exit_time="15:15:59",
                        stop_loss=.20, combined=False)
        ts = TimeStrategy(params, query)
        ts.strategy()
    except Exception as e:
        pass
    ts.copy_to_file()