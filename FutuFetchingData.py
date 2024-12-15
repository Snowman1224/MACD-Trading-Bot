from futu import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def fetch_futu_data(stock_code, start_date, end_date, ktype='K_30M', max_count=500):
    """
    Fetch historical K-line (candlestick) data from Futu OpenAPI.

    :param stock_code: The stock symbol, e.g., 'US.VOO'.
    :param start_date: Start date for historical data in 'YYYY-MM-DD' format.
    :param end_date: End date for historical data in 'YYYY-MM-DD' format.
    :param ktype: The type of K-line, e.g., 'K_30M' for 30-minute data.
    :param max_count: Maximum number of records to fetch in one request (default: 500).
    :return: A pandas DataFrame containing historical data.
    """

    "Input your own host and port number"
    quote_ctx = OpenQuoteContext(host='', port=00000)

    # Request historical data
    ret, data, page_req_key = quote_ctx.request_history_kline(stock_code, start=start_date, end=end_date, ktype=ktype,
                                                              max_count=max_count)

    if ret != RET_OK:
        print('Error:', data)
        quote_ctx.close()
        return None

    historical_data = data

    # Handle pagination
    while page_req_key is not None:
        ret, data, page_req_key = quote_ctx.request_history_kline(stock_code, start=start_date, end=end_date,
                                                                  ktype=ktype, max_count=max_count,
                                                                  page_req_key=page_req_key)
        if ret == RET_OK:
            historical_data = pd.concat([historical_data, data], ignore_index=True)
        else:
            print('Error:', data)
            break

    quote_ctx.close()

    # Return the DataFrame
    return historical_data

def process_futu_data(data):
    # Extract necessary columns
    data['Date'] = pd.to_datetime(data['time_key']).dt.date
    data['Time'] = pd.to_datetime(data['time_key']).dt.time
    data = data[['Date', 'Time', 'open', 'high', 'low', 'close']]
    data.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close']
    return data
