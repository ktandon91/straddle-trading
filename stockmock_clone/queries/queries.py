select_basis_ticker_and_date = """
select * from options_data where date = '{date}' and ticker in {ticker_names}
and time between '9:15:00' and '15:29:00';
"""

dummy_query = """
select * from options_data where date = '2018-05-11' and ticker = 'BANKNIFTY17MAY1822200PE.NFO' 
and time between '9:15:00' and '15:29:00'
"""

index_value_at_entry_time = """select open from index where date = '{date}' and time = '{time}' """

nearest_expiry = """
with date_selection as (select string_date, date, (date - '{date}') as date_diff from expiry_dates) 
select string_date from date_selection where date_diff >= 0 order by date_diff limit 1;
"""


## cte to convert string value dates to dates in postgres

# with string_dates as (select distinct(substring(ticker, 10,7)) as string_date
# from options_data where ticker like '%BANK%')
# select string_date, to_date(string_date,'DDMONYY') from string_dates

# ##CTE to insert into expiry table
# with string_dates as (select distinct(substring(ticker, 10,7)) as string_date
# from options_data where ticker like '%BANK%')
# insert into expiry_dates(string_date, date)
# select string_date, to_date(string_date,'DDMONYY') as date from string_dates