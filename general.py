import datetime

import plotly.express as px
import streamlit as st

import helper_st
import pandas as pd

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
        fig.update_traces(textfont_size=14,
                          textposition='outside', cliponaxis=False)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig.update_xaxes(
            linecolor='#fff',
        )
        # fig.update_yaxes(
        # )
    return fig

def best_shop_selling(df):
    # recent_day = df.loc[df.shape[0] - 1, 'scraping_day']

    # df_recent = df.loc[df['scraping_day'] == recent_day]

    best_selling = df.groupby(['shop_id'])['sold'].sum().reset_index()
    best_selling = best_selling[best_selling['sold'] != 0]

    return best_selling.nlargest(7, 'sold')
    
def best_product_selling(df):
    # recent_day = df.loc[df.shape[0] - 1, 'scraping_day']

    # df_recent = df.loc[df['scraping_day'] == recent_day]

    best_selling = df.groupby(['shop_id','item_id'])['sold'].sum().reset_index()
    best_selling = best_selling[best_selling['sold'] != 0]

    return best_selling.nlargest(15, 'sold')

def general():

    df = helper_st.get_data('/shopee-streamlit/data_with_tag')
    days = df['scraping_day'].unique().tolist()
    df['sale'] = ((df['price_max_before_discount'] +
                   df['price_min_before_discount']) // 2 * df['sold'])


    c1, c2 = st.columns((0.3, 0.8))
    with c1:
        time_option = st.selectbox(label='Choose Option: ', options=('Last Day', 'Last 7 Days', 'Total'))

    st.title('General Info')
    if time_option == 'Last Day':
        df, recent_day = helper_st.get_recent_day_data(df)

        st.caption(f'### Data From: {recent_day}')
    elif time_option == 'Last 7 Days':
        df, recent_days = helper_st.get_recent_7_days_data(df)

        st.caption(f'### Data From: {recent_days[-7]} to {recent_days[-1]}')
    else:
        st.caption(f"### Data From: {days[0]} to {days[-1]}")
    st.markdown('##')

    total_sales = ((df['price_max_before_discount'] +
                    df['price_min_before_discount']) // 2 * df['sold']).sum()
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
        st.subheader(helper_st.converse_currency(total_sales))
    with c3:
        st.subheader(f'Avg Per Order:')
        st.subheader(helper_st.converse_currency(average_order_value))

    st.markdown('---')
    st.subheader('Raw Data')
    see_data = st.expander('Click here to see the raw data 👉')
    with see_data:
        st.dataframe(data=df)


# -----------------------------------------------------------
    if time_option != 'Last Day':
        st.markdown('---')
        st.subheader('General')
        # fake_data = [
        #     {'scraping_day': '2023-02-20', 'sale': 172455000,
        #                    'sold': 610, 'avg': 172455000/610},
        #                    {'scraping_day': '2023-02-21', 'sale': 142455000,
        #                    'sold': 450, 'avg': 142455000/450},
        #                    {'scraping_day': '2023-02-22', 'sale': 145755000,
        #                    'sold': 700, 'avg': 145755000/700},
        #                    {'scraping_day': '2023-02-23', 'sale': 117255000,
        #                    'sold': 420, 'avg': 117255000/420},
        #                    {'scraping_day': '2023-02-27', 'sale': 186755000,
        #                    'sold': 923, 'avg': 186755000/923},
        #                    {'scraping_day': '2023-02-28', 'sale': 199255000,
        #                    'sold': 726, 'avg': 199255000/726},
        #                    {'scraping_day': '2023-02-26', 'sale': 133655000,
        #                    'sold': 623, 'avg': 133655000/623}
        # ]
        # fake_data = pd.DataFrame(fake_data)
        # df_g = pd.concat([df_g, fake_data], axis=0, ignore_index=True)
        df_g = df_g.sort_values('scraping_day')
        # general['avg'] = general['avg'].apply(math.ceil)
        # fig = px.line(
        #     data_frame=df_g,
        #     x='scraping_day',
        #     y='sale',
        #     markers=True
        # )
        # fig.update_xaxes(ticklabelmode="period", tickformat="%d\n%b %Y")
        # fig.update_layout(xaxis_range=[datetime.datetime(2023, 2, 15),
        #                                datetime.datetime(2023, 2, 28)])

        # st.plotly_chart(fig, use_container_width=False)



        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

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
        print(fig.layout)
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

# -----------------------------------------------------------
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
        color_ms = df.groupby(['tag_color'], dropna=False).size().reset_index(
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

        # shape_ms = df.groupby(['shape'], dropna=False).size().reset_index(
        #     name='count').sort_values('count', ascending=False)

        # fig = px.pie(shape_ms, values='count', names='shape',
        #              title='Shape')
        # fig = config_chart(fig=fig, type='pie')

        # st.plotly_chart(fig, use_container_width=True)

    with c2:
        category_ms = df.groupby(['category'], dropna=False).size().reset_index(
            name='count').sort_values('count', ascending=False)

        fig = px.pie(category_ms, values='count', names='category',
                     title='Category')
        fig = config_chart(fig=fig, type='pie')

        st.plotly_chart(fig, use_container_width=True)
    

    st.markdown('---')
    st.markdown('##')
    st.subheader('Best Selling')

    data = best_shop_selling(df)
    data['shop_id'] = data['shop_id'].apply(lambda x: f'shop id: {x}')
    print(data.dtypes)
    fig = px.bar(
        data_frame=data,
        x='shop_id',
        y='sold',
        title='Best Shop Selling',
        text='sold'
    )
    fig = config_chart(fig, 'bar')
    st.plotly_chart(fig, use_container_width=True)

    data = best_product_selling(df)
    # data['shop_id'] = data['shop_id'].apply(lambda x: f'shop id: {x}')
    print(data.dtypes)
    fig = px.bar(
        data_frame=data,
        x='item_id',
        y='sold',
        color='shop_id',
        title='Best Product Selling',
        text='sold'
    )
    fig = config_chart(fig, 'bar')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('---')
    st.subheader('Statistic')
    c1, c2 = st.columns(2)

    with c1:
        # Sold per category
        sold_per_category = df.groupby(['category'], dropna=False)['sold'].size().reset_index(
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
        sold_per_category_subcate = df.groupby(['category', 'sub_category'])['sold'].size().reset_index(
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

    # Sold per sub_category
    sold_per_category = df.groupby(['sub_category'], dropna=False)['sold'].size().reset_index(
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

    df['sale'] = ((df['price_max_before_discount'] +
                   df['price_min_before_discount']) // 2 * df['sold'])
    sales_per_category = df.groupby(['category'])['sale'].sum(
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
