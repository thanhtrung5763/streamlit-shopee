import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go


from html_test import POINT, PRODUCT_INFO, TABLE, product_info, product_tag
from general import general
import helper_st

BASE_IMG_URL = "https://cf.shopee.com.my/file/"


def config_chart(fig, type):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=50, r=50, b=70, t=70,),)
    fig.update_layout(
        title={
            'y':0.94,
            'x':0.03,
            'font_size': 18,
            'xanchor': 'left',
            'yanchor': 'top'}
    )
    if type == 'bar':
        fig.update_traces(textfont_size=12,
                          textposition='outside', cliponaxis=False)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig.update_xaxes(
            linecolor='#fff',
        )
        # fig.update_yaxes(
        # )
    return fig


def main():
    # @st.cache_data
    # def get_data(path):
    #     df = pd.read_csv(path, index_col=0, dtype={
    #                      'shop_id': str, 'sb_shop_id': str, 'ctime': str, })
    #     return df

    # def helper_st.converse_currency(num):
    #     return '₫ {:0,}'.format(num).replace(',', '.')

    with st.sidebar:
        menu = option_menu(
            menu_title='Main Menu',
            menu_icon='bar-chart-line-fill',
            options=['General', 'Shop Info', 'Product Info'],
            icons=['emoji-sunglasses-fill',
                   'emoji-expressionless-fill', 'emoji-smile-fill'],
            default_index=0,
            styles={
                "icon": { "font-size": "25px"},
                "nav-link-selected": {"background-color": "#636EFA"},
            }
        )
    if menu == 'General':
        general()
    elif menu == 'Shop Info':
        data = helper_st.get_data('/shopee-streamlit/data_with_tag_parquet', type='parquet')
        days = data['scraping_day'].unique().tolist()
        shop_id = '495701296'

        # SHOP INFO PAGE
        c1, c2 = st.columns((0.3, 0.8))
        with c1:
            shop_id = st.text_input('Input Shop ID: ', value='495701296')
            time_option = st.selectbox(label='Choose Option: ', options=('Last Day', 'Last 7 Days', 'Total'))

        st.title(f'SHOP ID: {shop_id}')
        if time_option == 'Last Day':
            df_selection, recent_day = helper_st.get_recent_day_data(data, shop_id)

            st.caption(f'### Data From: {recent_day}')
        elif time_option == 'Last 7 Days':
            df_selection, recent_days = helper_st.get_recent_7_days_data(data, shop_id)

            st.caption(f'### Data From: {recent_days[-7]} to {recent_days[-1]}')
        else:
            df_selection = data[data['shop_id'] == shop_id]
            st.caption(f"### Data From: {days[0]} to {days[-1]}")
        st.markdown("##")

        total_sales = ((df_selection['price_max_before_discount'] +
                        df_selection['price_min_before_discount']) // 2 * df_selection['sold']).sum()
        total_sold = int(df_selection['sold'].sum())
        average_order_value = total_sales // total_sold

        c1, c2, c3 = st.columns(3)

        with c1:
            st.subheader(f'Total Product Sold:')
            st.subheader(total_sold)
            # st.markdown(f'<h3 style="background-color:#16283b;border-radius:8px;padding:8px;">Total Product Sold:<br>{total_sold}</h3>', unsafe_allow_html=True)
        with c2:
            st.subheader(f'Total Sales:')
            st.subheader(helper_st.converse_currency(total_sales))
        with c3:
            st.subheader(f'Avg Per Order:')
            st.subheader(helper_st.converse_currency(average_order_value))
        # sold = data25.groupby(['shop_id'])['historical_sold'].sum(
        # ).reset_index().sort_values('historical_sold', ascending=False)
        # sold['shop_id'] = sold['shop_id'].astype(str)
        # print(sold)

        st.markdown('---')
        st.subheader('Raw Data')
        see_data = st.expander('Click here to see the raw data 👉')
        with see_data:
            st.dataframe(data=df_selection.reset_index(drop=True))

        st.markdown('---')
        st.subheader('Product Info')

        product_id = st.text_input(
            'Input item id:', placeholder='You can get item id from raw data above')
        c1, c2, c3= st.columns((0.1, 0.1, 0.8))
        with c1:
            show = st.button("Show Info")
        with c2:
            clear = st.button("Clear")
        if show:
            if product_id in df_selection['item_id'].values:
                product = df_selection[df_selection['item_id']
                                       == product_id].reset_index(drop=True)
                images = product['images'][0].strip(
                    '[]').replace("'", '').split(',')
                data = product.iloc[0].to_dict()
                # st.write(data)
                # st.write(image)
                # st.write(type(image))
                # st.write(product.dtypes)
                c1, c2 = st.columns((0.4, 0.6))
                with c1:
                    st.image(
                        f"{BASE_IMG_URL}{images[0]}",)
                    # st.markdown(f'{POINT}', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'{product_info(data)}',
                                unsafe_allow_html=True)
                    st.markdown(f'{product_tag(data)}', unsafe_allow_html=True)
        if clear:
            st.empty()
        st.markdown('---')
        st.subheader('Market Share')
        c1, c2 = st.columns(2)
        color_scheme = {"black": "#000000",
                        "white": "#FFFFFF",
                        "beige": "#F5F5DC",
                        "brown": "#964B00",
                        "red": "#FF0000",
                        "pink": "#FFC0CB",
                        "grey": "#808080",
                        "green": "#00FF00",
                        "blue": "#0000FF",
                        "navy": "#000080",
                        "yellow": "#FFFF00",
                        "purple": "#A020F0",
                        "orange": "#FFA500",
                        "khaki": "#c3b091",
                        "mint": "#3EB489",
                        "lavender": "#E6E6FA",
                        "wine": "#722F37",
                        "skyblue": "#87CEEB",
                        "null": "#FFF123"}
        # ms stands for market share
        with c1:
            color_ms = df_selection.groupby(['tag_color'], dropna=False).size().reset_index(
                name='count').sort_values('count', ascending=False)
            cs = []
            for color in color_ms['tag_color'].values:
                if color_scheme.get(color):
                    cs.append(color_scheme.get(color))

            fig = px.pie(color_ms, values='count', names='tag_color',
                         title='Color',
                         color_discrete_sequence=cs
                         )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig = config_chart(fig=fig, type='pie')

            st.plotly_chart(fig, use_container_width=True)

            # shape_ms = df_selection.groupby(['shape'], dropna=False).size().reset_index(
            #     name='count').sort_values('count', ascending=False)

            # fig = px.pie(shape_ms, values='count', names='shape',
            #              title='Shape')
            # fig = config_chart(fig=fig, type='pie')

            # st.plotly_chart(fig, use_container_width=True)

        with c2:
            category_ms = df_selection.groupby(['category'], dropna=False).size().reset_index(
                name='count').sort_values('count', ascending=False)

            fig = px.pie(category_ms, values='count', names='category',
                         title='Category')
            fig = config_chart(fig=fig, type='pie')

            st.plotly_chart(fig, use_container_width=True)

        st.markdown('---')
        st.subheader('Statistic')
        compare = st.radio('Compare with last 7 Days?', ('No', 'Yes'))
        
        c1, c2 = st.columns(2)

        with c1:
            if compare == 'Yes':
                recent_day = days[-7:]
                df_selection_7 = data.loc[data['scraping_day'].isin(recent_day)]
                df_selection_7 = df_selection_7[df_selection_7['shop_id'] == shop_id]
                # Sold per categoryrr
                sold_per_category = df_selection.groupby(['category'], dropna=False)['sold'].size().reset_index(
                    name='sold').sort_values('category', ascending=False)
                sold_per_category_7 = df_selection_7.groupby(['category'], dropna=False)['sold'].size().reset_index(
                    name='sold').sort_values('category', ascending=False)

                data = {
                    "model_1": sold_per_category['sold'].values.tolist(),
                    "model_2": sold_per_category_7['sold'].values.tolist(),
                    "labels": sold_per_category['category'].values.tolist()
                }
                fig2 = go.Figure(
                    data=[
                        go.Bar(
                            name="Last Day",
                            x=data["labels"],
                            y=data["model_1"],
                            offsetgroup=0,
                        ),
                        go.Bar(
                            name="Last 7 Days",
                            x=data["labels"],
                            y=data["model_2"],
                            offsetgroup=1,
                        ),
                    ],
                    layout=go.Layout(
                        title="Sold Per Category",
                        yaxis_title="Sold",
                        xaxis_title='Category'
                    )
                )    
                fig2 = config_chart(fig2, type='bar')
                st.plotly_chart(fig2, use_container_width=True)
            else:
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
                fig = config_chart(fig=fig, type='bar')

                st.plotly_chart(fig, use_container_width=True)

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

            fig = config_chart(fig=fig, type='bar')
            st.plotly_chart(fig, use_container_width=True)

        # with c3:
            # Sold per sub_category
        sold_per_category = df_selection.groupby(['sub_category'], dropna=False)['sold'].size().reset_index(
            name='count').sort_values('count', ascending=False)
        size = len(sold_per_category)
        if size > 10:
            size = 10
        # print(sold_per_category.loc[:size, :])
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

        df_selection['sale'] = ((df_selection['price_max_before_discount'] +
                                df_selection['price_min_before_discount']) // 2 * df_selection['sold'])
        sales_per_category = df_selection.groupby(['category'])['sale'].sum(
        ).reset_index(name='count').sort_values('count', ascending=True)
        sales_per_category['currency'] = sales_per_category['count'].apply(
            lambda x: helper_st.converse_currency(x))
        fig = px.bar(
            data_frame=sales_per_category,
            x='count',
            y='category',
            title='Sold Per Category',
            text='currency',
            orientation='h',
            labels={'count': 'Total Sales'},
        )
        x_range = int(sales_per_category.tail(1)['count'].values[0] * 1.1)
        fig = config_chart(fig=fig, type='bar')
        fig.update_traces(textfont_size=18)
        fig.update_layout(
            xaxis_range=[0, x_range]
        )
        st.plotly_chart(fig, use_container_width=True)
    elif menu == 'Product Info':
        def load_lottieurl(url):
                r = requests.get(url)
                if r.status_code != 200:
                    return None
                return r.json()
        from streamlit_lottie import st_lottie
        lottie_404_url = 'https://assets3.lottiefiles.com/packages/lf20_9Fhz02H45R.json'
        lottie_404 = load_lottieurl(lottie_404_url)
        st_lottie(lottie_404, height=800)
        # st.write('In Product Info')


if __name__ == '__main__':
    # shop_id = '70628044'
    st.set_page_config(page_title=f"Shopee Streamlit",
                       page_icon=":bar_chart:", layout="wide")
    with open('main.css') as style:
        st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)
    main()
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
