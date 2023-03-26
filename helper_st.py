import os
import glob
import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def get_data(path):
    
    extract_path = f'{os.getcwd()}{path}'
    files = glob.glob(os.path.join(extract_path, '*.csv'))
    li = []
    for file in files:
        f = open(file)
        df = pd.read_csv(f, dtype={'shop_id': str, 'sb_shop_id': str, 'ctime': str,})
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