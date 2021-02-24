import yaml
import numpy as np
import pandas as pd
from pandas import DataFrame
import PyPDF2
import requests
import re


with open("paths.yml", "r") as f:
    paths = yaml.load(f, Loader=yaml.FullLoader)

arkk_etf_url = paths["arkk_etf"]
arkq_etf_url = paths["arkq_etf"]
arkw_etf_url = paths["arkw_etf"]
arkg_etf_url = paths["arkg_etf"]
arkf_etf_url = paths["arkf_etf"]

def download_pdf(url, fund_name):
    response = requests.get(url)
    tmp_path = paths[f'{fund_name}_etf_path']
    
    with open(tmp_path, 'wb') as f:
        f.write(response.content)

def parse_etf_holdings_java(pdf_path: str):
    columns = [
        "NUM",
        "COMPANY",
        "TICKER",
        "CUSIP",
        "SHARES",
        "MARKET_VALUE($)",
        "WEIGHT(%)",
    ]

    df = tabula.read_pdf(pdf_path, pages=1, multiple_tables=False)
    # get first page

    columns_i = []

    for i in range(len(df[0].columns)):
        try:
            tbl_input = df[0].iloc[
                1, i
            ]  # use the first record of the table to determine cols
            val = np.isnan(tbl_input)
            if val:
                continue
            else:
                columns_i.append(i)
        except TypeError:
            columns_i.append(i)

    result_df = pd.DataFrame(data=df[0].iloc[:, columns_i])
    result_df.columns = columns

    return result_df

def parse_etf_holdings(pdf_path: str):
    columns = [
        "NUM",
        "COMPANY",
        "TICKER",
        "CUSIP",
        "SHARES",
        "MARKET_VALUE($)",
        "WEIGHT(%)",
    ]

    with open(pdf_path,'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        contents = reader.getPage(0).extractText()
    

    string_list = contents.split('\n')
    i = 8
    df_list = []
    try:
        while int(string_list[i]): # index of the row
            print('index', i)
            print(string_list[i:i+7])
            df_list.append(string_list[i:i+7])
            i += 7
    except ValueError: # EOF "The principal risks of investing"
        df = pd.DataFrame(df_list, columns = columns)
    
    return df

def check_columns(df: DataFrame):
    """
    If any of the columns don't have the correct types, fail loudly #TODO

    Parameters
    ----------
    df : DataFrame
        [description]
    """
    pass


def get_latest_date(pdf_path: str):
    """If any of the columns don't have the latest date, fail loudly #TODO - what time to check?

    Parameters
    ----------
    pdf_path : str
        [description]
    fund_name : str
        [description]
    """
    pdf_path = "./temp/arkf_etf.pdf"

    with open(pdf_path,'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        contents = reader.getPage(0).extractText()

    updated_as_of = re.search(r'(\d\d/\d\d/\d\d\d\d)',contents).group(1)

    return updated_as_of
    

def parse_email_table(html_string):
    
    print('parsing new email')
    results = pd.read_html(html_string)[0]
    results = results[1:]
    columns = ['Num', 'Fund', 'Date', 'Direction', 'Ticker', 'CUSIP', 'Company', 'Shares', '% of ETF']
    results.columns = columns

    print(results)
    return results

def get_all_etfs(latest:bool):
    
    all_etfs = paths['etf_names']

    all_results = pd.DataFrame()

    # DOWNLOAD PDFS
    if latest:
        print('Downloading all PDFs now')
        for name in all_etfs:
            url = paths[f'{name}_etf']        
            download_pdf(url, name) # save in temp folder
    
    # PARSE PDF
    for name in all_etfs:
        print(f'Parsing {name} PDF now')
        temp_path = paths[f'{name}_etf_path']
         
        result_df = parse_etf_holdings(temp_path)
        update_dt = get_latest_date(temp_path)
        result_df['FUND_NAME'] = name.upper()
        result_df['UPDATE_DT'] = update_dt
        print(f"{name} PDF updated as of {update_dt}")

        all_results = all_results.append(result_df,ignore_index=True)

        print(all_results)
    
    return all_results, update_dt

def compare(email_df: DataFrame, all_etf_df: DataFrame):
    all_etf_df = all_etf_df[~all_etf_df['TICKER'].isnull()]
    merged_df = pd.merge(email_df, all_etf_df, left_on=['Fund', 'Ticker'], right_on=['FUND_NAME','TICKER'] , how='left')
    cond = (merged_df['Direction'] == 'Buy') & (merged_df['TICKER'].isnull())
    exec_buy = merged_df[cond]
    
    return_cols = ['Fund', 'Ticker', 'Company']

    exec_buy = exec_buy[return_cols].sort_values(by='Fund')
    print(exec_buy)

    return exec_buy

def pretty_print(exec_buy: DataFrame, email_date: str, pdf_date: str):
    message = ""
    cols = ['Fund', 'Ticker', 'Company']
    for index, row in exec_buy.iterrows():
        comp = row['Company']
        ticker = row['Ticker']
        fund = row['Fund']
        message = message + f"{comp} ({ticker}) was added to {fund} \n"

    message = message + f"Email was received on {email_date} and pdfs were last updated on {pdf_date} \n"

    return message