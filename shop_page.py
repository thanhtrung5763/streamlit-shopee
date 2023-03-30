import streamlit as st
import app_helper
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app_constants import BASE_IMG_URL
from html_test import product_info, product_tag
def shop_page(df):
    days = df['scraping_day'].unique()
    c1, c2 = st.columns((0.3, 0.7))
    with c1:
        st.subheader('Shop ID:')
        shop_id = st.selectbox(
            label='Select Shop ID:',
            options=df['shop_id'].unique(),
            label_visibility='collapsed')
    with c2:
        st.subheader('Option:')
        time_option = st.selectbox(
            label='Select Range Of Data:',
            options=('Last Day', 'Last 7 Days', 'Total'),
            label_visibility='collapsed')

    if time_option == 'Last Day':
        df_selection, recent_day = app_helper.get_recent_day_data(
            df, shop_id)

        st.caption(f'### Data From: {recent_day}')
    elif time_option == 'Last 7 Days':
        df_selection, recent_days = app_helper.get_recent_7_days_data(
            df, shop_id)

        st.caption(
            f'### Data From: {recent_days[-7]} to {recent_days[-1]}')
    else:
        df_selection = df.loc[df['shop_id'] == shop_id].copy()
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
        st.subheader(app_helper.converse_currency(total_sales))
    with c3:
        st.subheader(f'Avg Per Order:')
        st.subheader(app_helper.converse_currency(average_order_value))

    st.markdown('---')
    st.subheader('Raw Data')
    see_data = st.expander('Click here to see the raw data 👉')
    with see_data:
        st.dataframe(data=df_selection.reset_index(drop=True))

    # --- PRODUCT INFO ---#
    st.markdown('---')
    st.subheader('Product Info')

    c1, c2 = st.columns((0.3, 0.7))
    with c1:
        product_id = st.selectbox(
            label='Select Product ID:',
            options=df_selection['item_id'].unique(),
            label_visibility='collapsed'
        )
    c1, c2, c3 = st.columns((0.1, 0.1, 0.8))
    with c1:
        show = st.button("Show")
    with c2:
        clear = st.button("Clear")
    if show:
        product = df_selection[df_selection['item_id']
                                == product_id].reset_index(drop=True)
        images = product['images'][0].strip(
            '[]').replace("'", '').split(',')
        data = product.iloc[0].to_dict()

        c1, c2 = st.columns((0.4, 0.6))
        with c1:
            st.image(
                f"{BASE_IMG_URL}{images[0]}",)
        with c2:
            st.markdown(f'{product_info(data)}',
                        unsafe_allow_html=True)
            st.markdown(f'{product_tag(data)}', unsafe_allow_html=True)
    if clear:
        st.empty()

    ### --- MARKET SHARE ---###
    st.markdown('---')
    st.subheader('Market Share')
    c1, c2 = st.columns(2)
    with c1:
        app_helper.plt_market_share_color(df_selection=df_selection)

    with c2:
        app_helper.plt_market_share_category(df_selection=df_selection)
    ### --- STATISTIC ---###
    if total_sold:
        st.markdown('---')
        st.subheader('Statistic')
        compare = st.radio('Compare with last 7 Days?', ('No', 'Yes'))

        c1, c2 = st.columns(2)
        with c1:
            if compare == 'Yes':
                recent_day = days[-7:]
                df_selection_7 = df_selection.loc[df_selection['scraping_day'].isin(
                    recent_day)]
                df_selection_7 = df_selection_7[df_selection_7['shop_id'] == shop_id]
                # Sold per category
                sold_per_category = df_selection.groupby(['category'], dropna=False)['sold'].sum(
                ).reset_index(name='sold').sort_values('category', ascending=False)
                sold_per_category_7 = df_selection_7.groupby(['category'], dropna=False)[
                    'sold'].sum().reset_index(name='sold').sort_values('category', ascending=False)

                data = {
                    "model_1": sold_per_category['sold'].values.tolist(),
                    "model_2": sold_per_category_7['sold'].values.tolist(),
                    "labels": sold_per_category['category'].values.tolist()
                }
                fig = go.Figure(
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
                fig = app_helper.config_chart(fig, type='bar')
                st.plotly_chart(fig)
            else:
                # Sold per category
                app_helper.plt_sold_per_category(df_selection=df_selection)
        with c2:
            # sold per category and sub_category
            app_helper.plt_sold_per_category_and_subcategory(df_selection=df_selection)
            
        # Sold per sub_category
        app_helper.plt_sold_per_subcategory(df_selection=df_selection)
        # Revenue per category
        app_helper.plt_revenue_per_category(df_selection=df_selection)