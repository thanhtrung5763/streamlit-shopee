import os
import glob
import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def get_data(path, type='csv'):

    li = []
    extract_path = f'{os.getcwd()}{path}'

    if type == 'csv':
        files = glob.glob(os.path.join(extract_path, '*.csv'))
        li = []
        print(len(files))
        for file in files:
            df = pd.read_csv(file, dtype={'shop_id': str, 'sb_shop_id': str, 'ctime': str,})
            li.append(df)
        files.clear()

        df = pd.concat(li, axis=0, ignore_index=True)
    elif type == 'parquet':
        files = glob.glob(os.path.join(extract_path, '*.parquet'))
        li = []
        print(len(files))
        for file in files:
            df = pd.read_parquet(file)
            li.append(df)
        files.clear()

        df = pd.concat(li, axis=0, ignore_index=True)
        
    df = df.sort_values('scraping_day')
    return df

@st.cache_data
def get_recent_day_data(data, shop_id=None):
    days = data['scraping_day'].unique().tolist()
    recent_day = days[-1]
    df_selection = data.loc[data['scraping_day'] == recent_day]
    if shop_id:
        df_selection = df_selection[df_selection['shop_id'] == shop_id]
    return df_selection, recent_day

@st.cache_data
def get_recent_7_days_data(data, shop_id=None):
    days = data['scraping_day'].unique().tolist()
    recent_days = days[-7:]
    df_selection = data.loc[data['scraping_day'].isin(recent_days)]
    if shop_id:
        df_selection = df_selection[df_selection['shop_id'] == shop_id]
    return df_selection, recent_days
        

def converse_currency(num):
    return '₫ {:0,}'.format(num).replace(',', '.')