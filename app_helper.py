import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import plotly_express as px
from app_constants import PRODUCT_COLOR_SCHEME


@st.cache_data
def get_data(path, type='csv'):

    li = []
    extract_path = f'{os.getcwd()}{path}'

    if type == 'csv':
        files = glob.glob(os.path.join(extract_path, '*.csv'))
        print(len(files))
        for file in files:
            df = pd.read_csv(file, dtype={'shop_id': str, 'sb_shop_id': str, 'ctime': str,})
            li.append(df)
        files.clear()

        df = pd.concat(li, axis=0, ignore_index=True)
    elif type == 'parquet':
        files = glob.glob(os.path.join(extract_path, '*.parquet'))
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

def config_chart(fig, type, direction='v'):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=50, r=50, b=70, t=70,),)
    fig.update_layout(
        title={
            'y': 0.94,
            'x': 0.03,
            'font_size': 18,
            'xanchor': 'left',
            'yanchor': 'top'}
    )
    if type == 'bar':
        fig.update_traces(textfont_size=12,
                          textposition='outside', cliponaxis=False)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        if direction == 'v':
            fig.update_xaxes(
                linecolor='#fff',
            )
        elif direction == 'h':
            fig.update_yaxes(
                linecolor='#fff'
            )
        # fig.update_yaxes(
        # )
    return fig

def plt_revenue_per_category(df_selection):
    if 'sale' not in list(df_selection):
        df_selection['sale'] = ((df_selection['price_max_before_discount'] +
                                df_selection['price_min_before_discount']) // 2 * df_selection['sold'])
    revenue_per_category = df_selection.groupby(['category'])['sale'].sum(
    ).reset_index(name='count').sort_values('count', ascending=True)
    revenue_per_category['currency'] = revenue_per_category['count'].apply(converse_currency)
    fig = px.bar(
        data_frame=revenue_per_category,
        x='count',
        y='category',
        title='Revenue Per Category',
        text='currency',
        orientation='h',
        labels={'count': 'Total Sales'},
    )
    x_range = int(revenue_per_category.tail(1)['count'].values[0] * 1.1)
    fig = config_chart(fig=fig, type='bar', direction='h')
    fig.update_traces(textfont_size=18)
    fig.update_layout(
        xaxis_range=[0, x_range],
    )
    st.plotly_chart(fig, use_container_width=True)

def plt_market_share_color(df_selection):
    color_ms = df_selection['tag_color'].value_counts().reset_index()
    color_ms.columns = ['tag_color', 'count']
    cs = []
    for color in color_ms['tag_color'].values:
        if PRODUCT_COLOR_SCHEME.get(color):
            cs.append(PRODUCT_COLOR_SCHEME.get(color))

    fig = px.pie(data_frame=color_ms,
                values='count',
                names='tag_color',
                title='Color',
                color_discrete_sequence=cs)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig = config_chart(fig=fig, type='pie')

    st.plotly_chart(fig, use_container_width=True)

def plt_market_share_category(df_selection):
    category_ms = df_selection['category'].value_counts().reset_index()
    category_ms.columns = ['category', 'count']

    fig = px.pie(data_frame=category_ms,
                values='count',
                names='category',
                title='Category')
    fig = config_chart(fig=fig, type='pie')

    st.plotly_chart(fig, use_container_width=True)

def plt_sold_per_category(df_selection):
    sold_per_category = df_selection.groupby(['category'], dropna=False)['sold'].sum(
    ).reset_index(name='sold').sort_values('category', ascending=False)
    fig = px.bar(
        data_frame=sold_per_category,
        x='category',
        y='sold',
        title='Sold Per Category',
        text='sold'
    )
    fig = config_chart(fig=fig, type='bar')
    # fig.update_traces(marker_line_color = '#636EFA', marker_line_width = 4)

    st.plotly_chart(fig, use_container_width=True)

def plt_sold_per_category_and_subcategory(df_selection):
    sold_per_category_subcate = df_selection.groupby(['category', 'sub_category'])['sold'].sum(
    ).reset_index(name='count').sort_values(['category', 'count', 'sub_category'], ascending=False)
    fig = px.bar(
        data_frame=sold_per_category_subcate,
        x='category',
        y='count',
        color='sub_category',
        title='Sold Per Category And Sub Category',
        text='count',
        labels={'count': 'Sold', 'sub_category': 'Sub Category'},
    )

    fig = config_chart(fig=fig, type='bar')
    st.plotly_chart(fig, use_container_width=True)
    
def plt_sold_per_subcategory(df_selection):
    sold_per_category = df_selection.groupby(['sub_category'], dropna=False)['sold'].sum().reset_index(
        name='count').sort_values('count', ascending=False)
    size = len(sold_per_category)
    if size > 10:
        size = 10
    fig = px.bar(
        data_frame=sold_per_category.head(size),
        x='sub_category',
        y='count',
        title='Sold Per Sub Category',
        text='count',
        labels={'count': 'Sold', 'sub_category': 'Sub Category'},
    )

    fig = config_chart(fig=fig, type='bar')
    st.plotly_chart(fig, use_container_width=True)

def plt_best_shop_selling(df_selection):
    fig = px.bar(
        data_frame=df_selection,
        x='shop_id',
        y='sold',
        title='Best Shop Selling',
        text='sold'
    )
    fig = config_chart(fig, 'bar')
    st.plotly_chart(fig, use_container_width=True)

def plt_best_product_selling(df_selection):
    fig = px.bar(
        data_frame=df_selection,
        x='item_id',
        y='sold',
        color='shop_id',
        title='Best Product Selling',
        text='sold'
    )
    fig = config_chart(fig, 'bar')
    st.plotly_chart(fig, use_container_width=True)