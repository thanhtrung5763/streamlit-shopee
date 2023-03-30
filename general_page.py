import streamlit as st
import app_helper
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def config_chart(fig, type, direction='v'):
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
        fig.update_traces(textfont_size=14,
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

def best_shop_selling(df):
    best_selling = df.groupby(['shop_id'])['sold'].sum().reset_index()
    best_selling = best_selling[best_selling['sold'] != 0]

    return best_selling.nlargest(7, 'sold')
    
def best_product_selling(df):
    # recent_day = df.loc[df.shape[0] - 1, 'scraping_day']

    # df_recent = df.loc[df['scraping_day'] == recent_day]

    best_selling = df.groupby(['shop_id','item_id'])['sold'].sum().reset_index()
    best_selling = best_selling[best_selling['sold'] != 0]

    return best_selling.nlargest(15, 'sold')

def general(df):

    days = df['scraping_day'].unique().tolist()
    df['sale'] = ((df['price_max_before_discount'] +
                   df['price_min_before_discount']) // 2 * df['sold'])


    c1, c2 = st.columns((0.3, 0.7))
    with c1:
        st.subheader('Option')
        time_option = st.selectbox(label='', options=('Last Day', 'Last 7 Days', 'Total'), label_visibility='collapsed')

    st.title('General Info')
    if time_option == 'Last Day':
        df, recent_day = app_helper.get_recent_day_data(df)

        st.caption(f'### Data From: {recent_day}')
    elif time_option == 'Last 7 Days':
        df, recent_days = app_helper.get_recent_7_days_data(df)

        st.caption(f'### Data From: {recent_days[-7]} to {recent_days[-1]}')
    else:
        st.caption(f"### Data From: {days[0]} to {days[-1]}")
    st.markdown('##')

    total_sales = (df['sale']).sum()
    total_sold = int(df['sold'].sum())
    average_order_value = total_sales // total_sold

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f'Total Product Sold:')
        st.subheader(total_sold)
        df_g = df.groupby(['scraping_day'])[['sale', 'sold']].sum().reset_index()
        df_g['avg'] = df_g['sale'] / df_g['sold']
        # last_sold  = df_g.loc[(df_g.shape[0] - 2), 'sold']
        # delta = int(last_sold / total_sold * 100)
        # st.metric('', total_sold, f'{delta} %', label_visibility='collapsed')
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
        st.dataframe(data=df)


# -----------------------------------------------------------
    if time_option != 'Last Day':
        st.markdown('---')
        st.subheader('General')

        fig = make_subplots(rows=1, cols=3, column_widths=[0.6, 0.2, 0.2], subplot_titles=['Sale', 'Sold', 'Avg'])

        fig.add_trace(
            go.Scatter(x=df_g['scraping_day'], y=df_g['sale'], name='sale'),
            row=1, col=1,
        )

        fig.add_trace(
            go.Scatter(x=df_g['scraping_day'], y=df_g['sold'], name='sold'),
            row=1, col=2
        )

        fig.add_trace(
            go.Scatter(x=df_g['scraping_day'], y=df_g['avg'], name='avg'),
            row=1, col=3
        )
        
        fig.update_layout(title_text="Sale, Sold and Avg")
        # fig.update_yaxes(
        #         gridcolor='#4f4f4f',
        #     )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=50, r=50, b=70, t=70,),)
        fig.update_layout(
        title={
            'y':0.95,
            'x':0.03,
            'font_size': 18,
            'xanchor': 'left',
            'yanchor': 'top'})
        # fig.update_xaxes(ticklabelmode="period", tickformat="%d\n%b %Y")
        # fig.update_layout(xaxis_range=[datetime.datetime(2023, 1, 15),
        #                                datetime.datetime(2023, 2, 20)])
        st.plotly_chart(fig, use_container_width=True)

    #--- MARKET SHARE ---#
    st.markdown('---')
    st.subheader('Market Share')
    c1, c2 = st.columns(2)

    with c1:
        app_helper.plt_market_share_color(df_selection=df)
    with c2:
        app_helper.plt_market_share_category(df_selection=df)

    st.markdown('---')
    st.markdown('##')
    st.subheader('Best Selling')

    data = best_shop_selling(df)
    data['shop_id'] = data['shop_id'].apply(lambda x: f'shop id: {x}')
    app_helper.plt_best_shop_selling(data)

    data = best_product_selling(df)
    app_helper.plt_best_product_selling(data)

    #--- STATISTIC ---#
    if total_sold:
        st.markdown('---')
        st.subheader('Statistic')
        c1, c2 = st.columns(2)

        with c1:
            # Sold per category
            app_helper.plt_sold_per_category(df_selection=df)
        with c2:
            # sold per category and sub_category
            app_helper.plt_sold_per_category_and_subcategory(df_selection=df)

        # Sold per sub_category
        app_helper.plt_sold_per_subcategory(df_selection=df)
        # Revenue per category
        app_helper.plt_revenue_per_category(df_selection=df)
