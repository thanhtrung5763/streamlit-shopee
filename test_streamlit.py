import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


def a(shop_id):
    shop_id = int(shop_id)

    @st.cache_data
    def get_data(path):
        df = pd.read_csv(path, index_col=0)
        return df

    def converse_currency(num):
        return '₫ {:0,}'.format(num).replace(',', '.')

    data24 = get_data('shopee-streamlit/sample_clothing_data_2023-02-24.csv')
    # data25 = get_data('shopee-streamlit/sample_clothing_data_2023-02-25.csv')

    df_selection = data24[data24['shop_id'] == shop_id]

    # SHOP INFO PAGE
    st.title(f'SHOP ID: {shop_id}')
    st.markdown("##")

    total_sales = ((df_selection['price_max_before_discount'] +
                    df_selection['price_min_before_discount']) // 2 * df_selection['sold']).sum()
    total_sold = int(df_selection['sold'].sum())
    average_order_value = total_sales // total_sold

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f'Total Product Sold:')
        st.subheader(total_sold)
    with c2:
        st.subheader(f'Total Sales:')
        st.subheader(converse_currency(total_sales))
    with c3:
        st.subheader(f'Avg Per Order:')
        st.subheader(converse_currency(average_order_value))
    # sold = data25.groupby(['shop_id'])['historical_sold'].sum(
    # ).reset_index().sort_values('historical_sold', ascending=False)
    # sold['shop_id'] = sold['shop_id'].astype(str)
    # print(sold)

    st.markdown('---')
    st.subheader('Market Share')
    c1, c2 = st.columns(2)
    # ms stands for market share
    with c1:
        color_ms = df_selection.groupby(['tag_color'], dropna=False).size().reset_index(
            name='count').sort_values('count', ascending=False)

        fig = px.pie(color_ms, values='count', names='tag_color',
                     title='Color')
        st.plotly_chart(fig, use_container_width=False)

        shape_ms = df_selection.groupby(['shape'], dropna=False).size().reset_index(
            name='count').sort_values('count', ascending=False)

        fig = px.pie(shape_ms, values='count', names='shape',
                     title='Shape')
        st.plotly_chart(fig, use_container_width=False)

    with c2:
        category_ms = df_selection.groupby(['category'], dropna=False).size().reset_index(
            name='count').sort_values('count', ascending=False)

        fig = px.pie(category_ms, values='count', names='category',
                     title='Category')
        st.plotly_chart(fig, use_container_width=False)

    c1, c2 = st.columns(2)

    with c1:
        # Sold per category
        sold_per_category = df_selection.groupby(['category'], dropna=False)['sold'].size().reset_index(
            name='sold').sort_values('category', ascending=False)
        fig = px.bar(
            data_frame=sold_per_category,
            x='category',
            y='sold',
            title='Sold Per Category',
            text='sold'
        )
        fig.update_traces(textfont_size=12, textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig)

        # Sold per sub_category
        sold_per_category = df_selection.groupby(['sub_category'], dropna=False)['sold'].size().reset_index(
            name='count').sort_values('count', ascending=False)
        fig = px.bar(
            data_frame=sold_per_category,
            x='sub_category',
            y='count',
            title='Sold Per Sub Category',
            text='count',
            labels={'count': 'Sold', 'sub_category': 'Sub Category'},
        )
        fig.update_traces(textfont_size=12,
                          textposition='outside', cliponaxis=False)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig)

    with c2:
        # sold per category and sub_category
        sold_per_category_subcate = df_selection.groupby(['category', 'sub_category'])['sold'].size().reset_index(
            name='count').sort_values(['category', 'count', 'sub_category'], ascending=False)
        fig = px.bar(
            data_frame=sold_per_category_subcate,
            x='category',
            y='count',
            color='sub_category',
            title='Sold Per Category And Sub Category',
            text='count',
            labels={'count': 'Sold', 'sub_category': 'Sub Category'},
        )
        fig.update_traces(textfont_size=12,
                          textposition='inside', cliponaxis=False)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig)

    df_selection['sale'] = ((df_selection['price_max_before_discount'] +
                            df_selection['price_min_before_discount']) // 2 * df_selection['sold'])
    sales_per_category = df_selection.groupby(['category'])['sale'].sum(
    ).reset_index(name='count').sort_values('count', ascending=True)
    sales_per_category['currency'] = sales_per_category['count'].apply(
        lambda x: converse_currency(x))
    fig = px.bar(
        data_frame=sales_per_category,
        x='count',
        y='category',
        title='Sold Per Category',
        text='currency',
        orientation='h',
        labels={'count': 'Total Sales'},
    )
    fig.update_traces(textfont_size=18)
    st.plotly_chart(fig)


if __name__ == '__main__':
    shop_id = 70628044
    st.set_page_config(page_title=f"{shop_id}",
                       page_icon=":bar_chart:", layout="wide")
    a(shop_id=shop_id)
# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)
