import tabula
import yaml
import numpy as np
import pandas as pd
import PyPDF2

with open("paths.yml", "r") as f:
    paths = yaml.load(f, Loader=yaml.FullLoader)

arkk_etf = paths["temp_arkk_etf"]
arkq_etf = paths["temp_arkq_etf"]
arkw_etf = paths["temp_arkw_etf"]
arkg_etf = paths["temp_arkg_etf"]
arkf_etf = paths["temp_arkf_etf"]

parse_etf_holdings(arkq_etf)


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


def check_columns(df: DataFrame):
    """
    If any of the columns don't have the correct types, fail loudly #TODO

    Parameters
    ----------
    df : DataFrame
        [description]
    """
    pass


def check_latest_date(pdf_path: str, fund_name: str):
    """If any of the columns don't have the latest date, fail loudly #TODO - what time to check?

    Parameters
    ----------
    pdf_path : str
        [description]
    fund_name : str
        [description]
    """
    pass
