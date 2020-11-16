import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import date

current_month = date.today().month
current_week = date.today().isocalendar()[1]

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
df['week'] = pd.to_datetime(df.index)
df['week'] = df['week'].dt.isocalendar().week

weeks_num_tech = [week for week in df['week'].unique()]
if current_week < 11 or len(weeks_num_tech) < 10:
    show_weeks_tech = weeks_num_tech[current_week - 1::-1]
else:
    list_week_tech = current_week - 10
    show_weeks_tech = weeks_num_tech[current_week - 1:list_week_tech:-1]

# Загружаем данные по посещению сайта
site_df = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
site_df.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
site_df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
site_df.set_index(site_df.columns[0], inplace=True)
site_df['month'] = pd.to_datetime(site_df.index)
site_df['month'] = site_df['month'].dt.month
site_df['week'] = pd.to_datetime(site_df.index)
site_df['week'] = site_df['week'].dt.isocalendar().week

weeks_num_site = [week for week in site_df['week'].unique()]
if current_week < 11 or len(weeks_num_site) < 10:
    show_weeks_site = weeks_num_site[current_week - 1::-1]
else:
    list_week_site = current_week - 10
    show_weeks_site = weeks_num_site[current_week - 1:list_week_site:-1]

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
            dcc.Slider(id='week-slider_users',
                       min=min(show_weeks_tech),
                       max=max(show_weeks_tech),
                       value=current_week,
                       marks={str(week): str(week) for week in show_weeks_tech},
                       step=None)
        ], className='six columns'),
        html.Div([
            html.Center(html.H3('Сопровождение пользователей')),
            dcc.Graph(id='tech'),
            dcc.Slider(id='week-slider_tech',
                       min=min(show_weeks_tech),
                       max=max(show_weeks_tech),
                       value=current_week,
                       marks={str(week): str(week) for week in show_weeks_tech},
                       step=None)
        ], className='six columns'),
    ], className='row'),
    html.Div([
        html.Div([
            html.H3(children="Статистика посещаний разделов сайта")
        ], className='zagolovok'),
        html.Div([
            dcc.Graph(id='site'),
            dcc.Slider(id='week-slider_site',
                       min=min(show_weeks_site),
                       max=max(show_weeks_site),
                       value=current_week,
                       marks={str(week): str(week) for week in show_weeks_site},
                       step=None)
        ])
    ], className='eleven columns')
], className='row')


@app.callback(
    Output('users', 'figure'),
    [Input('week-slider_users', 'value')])
def update_figure_user(selected_week_user):
    df1 = pd.read_excel('data.xlsx', skiprows=7)
    df1 = df1.drop('Unnamed: 0', axis=1)
    df1.set_index(df1.columns[0], inplace=True)
    df1 = df1.T
    df1['month'] = pd.to_datetime(df1.index)
    df1['month'] = df1['month'].dt.month
    df1['week'] = pd.to_datetime(df1.index)
    df1['week'] = df1['week'].dt.isocalendar().week

    filtered_df_1 = df1[df1['week'] == selected_week_user]

    trace_office = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя в офисе']),
                              name='работа в офисе',
                              mode='lines+markers',
                              marker=dict(size=15),
                              line=dict(color='crimson', width=5))
    trace_online = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя на удаленной работе']),
                              name='удаленная работа',
                              mode='lines+markers',
                              marker=dict(size=15),
                              line=dict(color='lightslategrey', width=5))

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
            x=0,
            xanchor='left',
            y=1.35,
            yanchor='top'
        )
    ])

    layout_user = dict(
        updatemenus=updatemenus,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1)
    )

    return {
        "data": data_user,
        "layout": layout_user}


@app.callback(
    Output('tech', 'figure'),
    [Input('week-slider_tech', 'value')])
def update_figure_tech(selected_week_tech):
    df2 = pd.read_excel('data.xlsx', skiprows=7)
    df2 = df2.drop('Unnamed: 0', axis=1)
    df2.set_index(df2.columns[0], inplace=True)
    df2 = df2.T
    df2['month'] = pd.to_datetime(df2.index)
    df2['month'] = df2['month'].dt.month
    df2['week'] = pd.to_datetime(df2.index)
    df2['week'] = df2['week'].dt.isocalendar().week

    filtered_df_2 = df2[df2['week'] == selected_week_tech]

    trace_rtk = go.Scatter(x=list(filtered_df_2.index),
                           y=list(filtered_df_2['РТК']),
                           name='РТК',
                           mode='lines+markers',
                           marker=dict(size=15),
                           line=dict(color='#F44242', width=5))

    trace_sue = go.Scatter(x=list(filtered_df_2.index),
                           y=list(filtered_df_2['СУЭ']),
                           name='СУЭ',
                           mode='lines+markers',
                           marker=dict(size=15),
                           line=dict(color='green', width=5))

    trace_sue_osp = go.Scatter(x=list(filtered_df_2.index),
                               y=list(filtered_df_2['СУЭ ОСП']),
                               name='СУЭ ОСП',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='blue', width=5))

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
            x=0,
            xanchor='left',
            y=1.35,
            yanchor='top'
        )
    ])

    layout_tech = dict(
        # title='Сопроводение пользователей',
        updatemenus=updatemenus,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1)
    )

    return {
        "data": data_tech,
        "layout": layout_tech
    }


@app.callback(
    Output('site', 'figure'),
    [Input('week-slider_site', 'value')])
def update_figure_site(selected_week_site):
    site_df_upd = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
    site_df_upd.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
    site_df_upd.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    site_df_upd.set_index(site_df_upd.columns[0], inplace=True)
    site_df_upd['month'] = pd.to_datetime(site_df_upd.index)
    site_df_upd['month'] = site_df_upd['month'].dt.month
    site_df_upd['week'] = pd.to_datetime(site_df_upd.index)
    site_df_upd['week'] = site_df_upd['week'].dt.isocalendar().week

    filtered_site_df = site_df_upd[site_df_upd['week'] == selected_week_site]

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
        autosize=True
    )

    return {
        "data": data_site,
        "layout": layout_site
    }


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.109', port=8060)
