import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import date


current_month = date.today().month
# Текущий формат файла с отчетом (горизонтальная таблица)
# df = pd.read_excel('data.xlsx', skiprows=7)
# df = df.drop('Unnamed: 0', axis=1)
# df.set_index(df.columns[0], inplace=True)
# df = df.T
# df['month'] = pd.to_datetime(df.index)
# df['month'] = df['month'].dt.month

# Предлагаемый формат файла с отчетом (вертикальная таблица)
df = pd.read_excel('data.xlsx', sheet_name='Данные')
df.set_index(df.columns[0], inplace=True)
df['month'] = pd.to_datetime(df.index)
df['month'] = df['month'].dt.month

# Загружаем данные по посещению сайта
site_df = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
site_df.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
site_df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
site_df.set_index(site_df.columns[0], inplace=True)
site_df['month'] = pd.to_datetime(site_df.index)
site_df['month'] = site_df['month'].dt.month


external_stylesheets = ['assets/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        # html.H1("Межрегиональное бухгалтерское УФК"),
        html.H2('Отчет о работе Отдела сопровождения пользователей'),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            html.Center(html.H3('Обращения в тех поддержку')),
            dcc.Graph(id='users'),
            dcc.Slider(id='month-slider_users',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=current_month,
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ], className='six columns'),
        html.Div([
            html.Center(html.H3('Сопровождение пользователей')),
            dcc.Graph(id='tech'),
            dcc.Slider(id='month-slider_tech',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=current_month,
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ], className='six columns'),
    ], className='row'),
    html.Div([
        html.Div([
            html.H3(children="Статистика посещаний разделов сайта")
        ], className='zagolovok'),
        html.Div([
            dcc.Graph(id='site'),
            dcc.Slider(id='month-slider_site',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=current_month,
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ])
    ], className='eleven columns')
], className='row')


@app.callback(
    Output('users', 'figure'),
    [Input('month-slider_users', 'value')])
def update_figure_user(selected_month_user):
    df1 = pd.read_excel('data.xlsx', skiprows=7)
    df1 = df1.drop('Unnamed: 0', axis=1)
    df1.set_index(df1.columns[0], inplace=True)
    df1 = df1.T
    df1['month'] = pd.to_datetime(df1.index)
    df1['month'] = df1['month'].dt.month

    filtered_df_1 = df1[df1['month'] == selected_month_user]

    trace_office = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя в офисе']),
                              name='работа в офисе',
                              line=dict(color='crimson', width=3))
    trace_online = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя на удаленной работе']),
                              name='удаленная работа',
                              line=dict(color='lightslategrey', width=3))

    trace_offline_bar = go.Bar(x=list(filtered_df_1.index),
                               y=list(filtered_df_1['Сопровождение пользователя в офисе']),
                               base=0,
                               marker_color='crimson',
                               name='работа в офисе',
                               visible=False)

    trace_online_bar = go.Bar(x=filtered_df_1.index,
                              y=list(filtered_df_1['Сопровождение пользователя на удаленной работе']),
                              base=0,
                              marker_color='lightslategrey',
                              name='удаленная работа',
                              visible=False)

    data_user = [trace_office, trace_online, trace_offline_bar, trace_online_bar]

    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{'visible': [True, True, False, False]}],
                    label='Линейный график',
                    metod='update'
                ),
                dict(
                    args=[{'visible': [False, False, True, True]}],
                    label='Столбчатая диаграмма',
                    metod='update'
                )
            ]),
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.5,
            xanchor='left',
            y=1.25,
            yanchor='top'
        )
    ])

    layout_user = dict(
        title='Обращения в техническую поддержку',
        updatemenus=updatemenus,
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=14,
                         label='2w',
                         step='day',
                         stepmode='backward'),
                    dict(count=21,
                         label='3w',
                         step='day',
                         stepmode='backward'),
                    dict(count=28,
                         label='4w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date_user'
        )
    )

    return {
        "data": data_user,
        "layout": layout_user}


@app.callback(
    Output('tech', 'figure'),
    [Input('month-slider_tech', 'value')])
def update_figure_tech(selected_month_tech):
    df2 = pd.read_excel('data.xlsx', skiprows=7)
    df2 = df2.drop('Unnamed: 0', axis=1)
    df2.set_index(df2.columns[0], inplace=True)
    df2 = df2.T
    df2['month'] = pd.to_datetime(df2.index)
    df2['month'] = df2['month'].dt.month

    filtered_df_2 = df2[df2['month'] == selected_month_tech]

    trace_rtk = go.Scatter(x=list(filtered_df_2.index),
                           y=list(filtered_df_2['РТК']),
                           name='РТК',
                           line=dict(color='#F44242', width=3))

    trace_sue = go.Scatter(x=list(filtered_df_2.index),
                           y=list(filtered_df_2['СУЭ']),
                           name='СУЭ',
                           line=dict(color='green', width=3))

    trace_sue_osp = go.Scatter(x=list(filtered_df_2.index),
                               y=list(filtered_df_2['СУЭ ОСП']),
                               name='СУЭ ОСП',
                               line=dict(color='blue', width=3))

    trace_rtk_bar = go.Bar(x=filtered_df_2.index,
                           y=filtered_df_2['РТК'],
                           base=0,
                           marker_color='#F44242',
                           name='РТК',
                           visible=False)

    trace_sue_bar = go.Bar(x=filtered_df_2.index,
                           y=filtered_df_2['СУЭ'],
                           base=0,
                           marker_color='green',
                           name='СУЭ',
                           visible=False)

    trace_sue_osp_bar = go.Bar(x=filtered_df_2.index,
                               y=filtered_df_2['СУЭ ОСП'],
                               base=0,
                               marker_color='blue',
                               visible=False)

    data_tech = [trace_rtk, trace_sue, trace_sue_osp, trace_rtk_bar, trace_sue_bar, trace_sue_osp_bar]

    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{'visible': [True, True, True, False, False, False]}],
                    label='Линейный график',
                    metod='update'
                ),
                dict(
                    args=[{'visible': [False, False, False, True, True, True]}],
                    label='Столбчатая диаграмма',
                    metod='update'
                )
            ]),
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0.5,
            xanchor='left',
            y=1.25,
            yanchor='top'
        )
    ])

    layout_tech = dict(
        title='Сопроводение пользователей',
        updatemenus=updatemenus,
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=14,
                         label='2w',
                         step='day',
                         stepmode='backward'),
                    dict(count=21,
                         label='3w',
                         step='day',
                         stepmode='backward'),
                    dict(count=28,
                         label='4w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date_user'
        )
    )

    return {
        "data": data_tech,
        "layout": layout_tech
    }


@app.callback(
    Output('site', 'figure'),
    [Input('month-slider_site', 'value')])
def update_figure_site(selected_month_site):
    site_df_upd = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
    site_df_upd.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
    site_df_upd.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    site_df_upd.set_index(site_df_upd.columns[0], inplace=True)
    site_df_upd['month'] = pd.to_datetime(site_df_upd.index)
    site_df_upd['month'] = site_df_upd['month'].dt.month

    filtered_site_df = site_df_upd[site_df_upd['month'] == selected_month_site]

    trace_budget_bar = go.Bar(x=filtered_site_df.index,
                              y=filtered_site_df['Электронный бюджет'],
                              base=0,
                              # marker_color='#F44242',
                              name='Электронный бюджет')

    trace_news_bar = go.Bar(x=filtered_site_df.index,
                            y=filtered_site_df['Новости'],
                            base=0,
                            # marker_color='green',
                            name='Новости')

    trace_about_bar = go.Bar(x=filtered_site_df.index,
                             y=filtered_site_df['О межрегиональном бухгалтерском УФК'],
                             base=0,
                             # marker_color='blue',
                             name='О межрегиональном бухгалтерском УФК')

    trace_other_bar = go.Bar(x=filtered_site_df.index,
                             y=filtered_site_df['Иная деятельность'],
                             base=0,
                             # marker_color='blue',
                             name='Иная деятельность')

    data_site = [trace_budget_bar, trace_news_bar, trace_about_bar, trace_other_bar]

    layout_site = dict(
        title='Статистика посещаний разделов сайта',
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=14,
                         label='2w',
                         step='day',
                         stepmode='backward'),
                    dict(count=21,
                         label='3w',
                         step='day',
                         stepmode='backward'),
                    dict(count=28,
                         label='4w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date_site'
        )
    )

    return {
        "data": data_site,
        "layout": layout_site
    }


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.10', port=8050)
