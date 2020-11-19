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


def eval_expression(input_string):
    """Эта функция полностью запрещает использование имен в eval(). (В целях безопасности)"""
    code = compile(input_string, "<string>", "eval")
    if code.co_names:
        raise NameError(f"Использование имён запрещено.")
    return eval(code, {"__builtins__": {}}, {})


app.layout = html.Div([
    html.Div([
        # html.H1("Межрегиональное бухгалтерское УФК"),
        html.H2('Отчет о работе Отдела сопровождения пользователей'),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            dcc.Tabs(id='choice_period', value='weeks', children=[
                dcc.Tab(label='Неделя', value='weeks', children=[
                    html.Div([
                        html.Div([
                            html.Center(html.H3('Обращения в тех поддержку')),
                            dcc.Dropdown(id='user_dropdown_week',
                                         options=[
                                             dict(label='Линейный график', value='[True, True, False, False]'),
                                             dict(label='Столбчатая диаграмма', value='[False, False, True, True]')],
                                         value='[True, True, False, False]',
                                         clearable=False,
                                         searchable=False,
                                         style=dict(width='250px', margin='30px, 0px')),
                            dcc.Graph(id='users_week'),
                            dcc.Slider(id='week-slider_users',
                                       min=min(show_weeks_tech),
                                       max=max(show_weeks_tech),
                                       value=current_week,
                                       marks={str(week): str(week) for week in show_weeks_tech},
                                       step=None)
                        ], className='six columns'),
                        html.Div([
                            html.Center(html.H3('Сопровождение пользователей')),
                            dcc.Dropdown(id='tech_dropdown_week',
                                         options=[
                                             dict(label='Линейный график', value='[True, True, True, False, False, '
                                                                                 'False]'),
                                             dict(label='Столбчатая диаграмма', value='[False, False, False, True, '
                                                                                      'True, True]')],
                                         value='[True, True, True, False, False, False]',
                                         clearable=False,
                                         searchable=False,
                                         style=dict(width='250px', margin='30px, 0px')),
                            dcc.Graph(id='tech_week'),
                            dcc.Slider(id='week-slider_tech',
                                       min=min(show_weeks_tech),
                                       max=max(show_weeks_tech),
                                       value=current_week,
                                       marks={str(week): str(week) for week in show_weeks_tech},
                                       step=None)
                        ], className='six columns'),
                    ], className='row'),
                    html.Div([
                        html.H3(children="Статистика посещаний разделов сайта")
                    ], className='zagolovok'),
                    html.Div([
                        dcc.Dropdown(id='dropdown_site_week',
                                     value='[True, True, True, True, False, False, False, False]',
                                     options=[
                                         dict(label='Столбчатая диаграмма', value='[True, True, True, True, False, '
                                                                                  'False, False, False]'),
                                         dict(label='Линейный график', value='[False, False, False, False, True, '
                                                                             'True, True, True]')],
                                     clearable=False,
                                     searchable=False,
                                     className='dropdown',
                                     style=dict(width='250px', margin='30px, 0px')),
                        dcc.Graph(id='site_week'),
                        dcc.Slider(id='slider_site_week',
                                   min=min(show_weeks_site),
                                   max=max(show_weeks_site),
                                   value=current_week,
                                   marks={str(week): str(week) for week in show_weeks_site},
                                   step=None)
                    ], className='eleven columns')
                ]),
                dcc.Tab(label='Месяц', value='months', children=[
                    html.Div([
                        html.Div([
                            html.Center(html.H3('Обращения в тех поддержку')),
                            dcc.Dropdown(id='user_dropdown_month',
                                         options=[
                                             dict(label='Линейный график', value='[True, True, False, False]'),
                                             dict(label='Столбчатая диаграмма', value='[False, False, True, True]')],
                                         value='[True, True, False, False]',
                                         clearable=False,
                                         searchable=False,
                                         style=dict(width='250px', margin='30px, 0px')),
                            dcc.Graph(id='users_month'),
                            dcc.Slider(id='month-slider_users',
                                       min=df['month'].min(),
                                       max=df['month'].max(),
                                       value=current_month,
                                       marks={str(month): str(month) for month in df['month'].unique()},
                                       step=None)
                        ], className='six columns'),
                        html.Div([
                            html.Center(html.H3('Сопровождение пользователей')),
                            dcc.Dropdown(id='tech_dropdown_month',
                                         options=[
                                             dict(label='Линейный график', value='[True, True, True, False, False, '
                                                                                 'False]'),
                                             dict(label='Столбчатая диаграмма', value='[False, False, False, True, '
                                                                                      'True, True]')],
                                         value='[True, True, True, False, False, False]',
                                         clearable=False,
                                         searchable=False,
                                         style=dict(width='250px', margin='30px, 0px')),
                            dcc.Graph(id='tech_month'),
                            dcc.Slider(id='month-slider_tech',
                                       min=df['month'].min(),
                                       max=df['month'].max(),
                                       value=current_month,
                                       marks={str(month): str(month) for month in df['month'].unique()},
                                       step=None)
                        ], className='six columns'),
                    ], className='row'),
                    html.Div([
                        html.H3(children="Статистика посещаний разделов сайта")
                    ], className='zagolovok'),
                    html.Div([
                        dcc.Dropdown(id='dropdown_site_month',
                                     value='[True, True, True, True, False, False, False, False]',
                                     options=[
                                         dict(label='Столбчатая диаграмма', value='[True, True, True, True, False, '
                                                                                  'False, False, False]'),
                                         dict(label='Линейный график',
                                              value='[False, False, False, False, True, True, True, True]')],
                                     clearable=False,
                                     searchable=False,
                                     className='dropdown',
                                     style=dict(width='250px', margin='30px, 0px')),
                        dcc.Graph(id='site_month'),
                        dcc.Slider(id='slider_site_month',
                                   min=df['month'].min(),
                                   max=df['month'].max(),
                                   value=current_month,
                                   marks={str(month): str(month) for month in df['month'].unique()},
                                   step=None)
                    ], className='eleven columns')
                ]), ]),
            html.Div(id='tabs_content')
        ])
    ])
])


@app.callback(
    Output('users_week', 'figure'),
    Output('users_month', 'figure'),
    [Input('choice_period', 'value'),
     Input('week-slider_users', 'value'),
     Input('user_dropdown_week', 'value'),
     Input('month-slider_users', 'value'),
     Input('user_dropdown_month', 'value')
     ])
def update_figure_user(tab, selected_week_user, figure_user_type, selected_month_user, figure_user_type_month):
    df1 = pd.read_excel('data.xlsx', skiprows=7)
    df1 = df1.drop('Unnamed: 0', axis=1)
    df1.set_index(df1.columns[0], inplace=True)
    df1 = df1.T
    df1['month'] = pd.to_datetime(df1.index)
    df1['month'] = df1['month'].dt.month
    df1['week'] = pd.to_datetime(df1.index)
    df1['week'] = df1['week'].dt.isocalendar().week

    filtered_df_week = df1[df1['week'] == selected_week_user]
    filtered_df_month = df1[df1['month'] == selected_month_user]

    if tab == 'weeks':
        figure_user_type = eval_expression(figure_user_type)
        trace_office = go.Scatter(x=list(filtered_df_week.index),
                                  y=list(filtered_df_week['Сопровождение пользователя в офисе']),
                                  name='работа в офисе',
                                  mode='lines+markers',
                                  marker=dict(size=15),
                                  line=dict(color='crimson', width=5),
                                  visible=figure_user_type[0])
        trace_online = go.Scatter(x=list(filtered_df_week.index),
                                  y=list(filtered_df_week['Сопровождение пользователя на удаленной работе']),
                                  name='удаленная работа',
                                  mode='lines+markers',
                                  marker=dict(size=15),
                                  line=dict(color='lightslategrey', width=5),
                                  visible=figure_user_type[1])
        trace_offline_bar = go.Bar(x=list(filtered_df_week.index),
                                   y=list(filtered_df_week['Сопровождение пользователя в офисе']),
                                   base=0,
                                   marker=dict(color='crimson'),
                                   name='работа в офисе',
                                   visible=figure_user_type[2])
        trace_online_bar = go.Bar(x=filtered_df_week.index,
                                  y=list(filtered_df_week['Сопровождение пользователя на удаленной работе']),
                                  base=0,
                                  marker=dict(color='lightslategrey'),
                                  name='удаленная работа',
                                  visible=figure_user_type[3])

        data_user = [trace_office, trace_online, trace_offline_bar, trace_online_bar]

        layout_user = dict(
            autosize=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1),
        )

        return [{
            "data": data_user,
            "layout": layout_user}, {
            "data": data_user,
            "layout": layout_user}]

    elif tab == 'months':
        figure_user_type_month = eval_expression(figure_user_type_month)
        trace_office = go.Scatter(x=list(filtered_df_month.index),
                                  y=list(filtered_df_month['Сопровождение пользователя в офисе']),
                                  name='работа в офисе',
                                  mode='lines+markers',
                                  marker=dict(size=15),
                                  line=dict(color='crimson', width=5),
                                  visible=figure_user_type_month[0])
        trace_online = go.Scatter(x=list(filtered_df_month.index),
                                  y=list(filtered_df_month['Сопровождение пользователя на удаленной работе']),
                                  name='удаленная работа',
                                  mode='lines+markers',
                                  marker=dict(size=15),
                                  line=dict(color='lightslategrey', width=5),
                                  visible=figure_user_type_month[1])
        trace_offline_bar = go.Bar(x=list(filtered_df_month.index),
                                   y=list(filtered_df_month['Сопровождение пользователя в офисе']),
                                   base=0,
                                   marker=dict(color='crimson'),
                                   name='работа в офисе',
                                   visible=figure_user_type_month[2])
        trace_online_bar = go.Bar(x=filtered_df_month.index,
                                  y=list(filtered_df_month['Сопровождение пользователя на удаленной работе']),
                                  base=0,
                                  marker=dict(color='lightslategrey'),
                                  name='удаленная работа',
                                  visible=figure_user_type_month[3])

        data_user = [trace_office, trace_online, trace_offline_bar, trace_online_bar]

        layout_user = dict(
            autosize=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1),
        )

        return [{
            "data": data_user,
            "layout": layout_user}, {
            "data": data_user,
            "layout": layout_user}]


@app.callback(
    Output('tech_week', 'figure'),
    Output('tech_month', 'figure'),
    [Input('choice_period', 'value'),
     Input('week-slider_tech', 'value'),
     Input('tech_dropdown_week', 'value'),
     Input('month-slider_tech', 'value'),
     Input('tech_dropdown_month', 'value')
     ])
def update_figure_tech(tab, selected_week_tech, figure_tech_type, selected_month_tech, figure_tech_type_month):
    df2 = pd.read_excel('data.xlsx', skiprows=7)
    df2 = df2.drop('Unnamed: 0', axis=1)
    df2.set_index(df2.columns[0], inplace=True)
    df2 = df2.T
    df2['month'] = pd.to_datetime(df2.index)
    df2['month'] = df2['month'].dt.month
    df2['week'] = pd.to_datetime(df2.index)
    df2['week'] = df2['week'].dt.isocalendar().week

    filtered_df_week = df2[df2['week'] == selected_week_tech]
    filtered_df_month = df2[df2['month'] == selected_month_tech]

    if tab == 'weeks':
        figure_tech_type = eval_expression(figure_tech_type)

        trace_rtk = go.Scatter(x=list(filtered_df_week.index),
                               y=list(filtered_df_week['РТК']),
                               name='РТК',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='#67b18d', width=5),
                               visible=figure_tech_type[0])

        trace_sue = go.Scatter(x=list(filtered_df_week.index),
                               y=list(filtered_df_week['СУЭ']),
                               name='СУЭ',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='#5794a1', width=5),
                               visible=figure_tech_type[1])

        trace_sue_osp = go.Scatter(x=list(filtered_df_week.index),
                                   y=list(filtered_df_week['СУЭ ОСП']),
                                   name='СУЭ ОСП',
                                   mode='lines+markers',
                                   marker=dict(size=15),
                                   line=dict(color='#9b5050', width=5),
                                   visible=figure_tech_type[2])

        trace_rtk_bar = go.Bar(x=filtered_df_week.index,
                               y=filtered_df_week['РТК'],
                               base=0,
                               marker=dict(color='#67b18d'),
                               name='РТК',
                               visible=figure_tech_type[3])

        trace_sue_bar = go.Bar(x=filtered_df_week.index,
                               y=filtered_df_week['СУЭ'],
                               base=0,
                               marker=dict(color='#5794a1'),
                               name='СУЭ',
                               visible=figure_tech_type[4])

        trace_sue_osp_bar = go.Bar(x=filtered_df_week.index,
                                   y=filtered_df_week['СУЭ ОСП'],
                                   base=0,
                                   marker=dict(color='#9b5050'),
                                   visible=figure_tech_type[5])

        data_tech = [trace_rtk, trace_sue, trace_sue_osp, trace_rtk_bar, trace_sue_bar, trace_sue_osp_bar]

        layout_tech = dict(
            autosize=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1),
        )

        return [{
            "data": data_tech,
            "layout": layout_tech}, {
            "data": data_tech,
            "layout": layout_tech}]

    elif tab == 'months':
        figure_user_tech_month = eval_expression(figure_tech_type_month)

        trace_rtk = go.Scatter(x=filtered_df_month.index,
                               y=filtered_df_month['РТК'],
                               name='РТК',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='#67b18d', width=5),
                               visible=figure_user_tech_month[0])

        trace_sue = go.Scatter(x=filtered_df_month.index,
                               y=filtered_df_month['СУЭ'],
                               name='СУЭ',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='#5794a1', width=5),
                               visible=figure_user_tech_month[1])

        trace_sue_osp = go.Scatter(x=filtered_df_week.index,
                                   y=filtered_df_week['СУЭ ОСП'],
                                   name='СУЭ ОСП',
                                   mode='lines+markers',
                                   marker=dict(size=15),
                                   line=dict(color='#9b5050', width=5),
                                   visible=figure_user_tech_month[2])

        trace_rtk_bar = go.Bar(x=filtered_df_month.index,
                               y=filtered_df_month['РТК'],
                               base=0,
                               marker=dict(color='#67b18d'),
                               name='РТК',
                               visible=figure_user_tech_month[3])

        trace_sue_bar = go.Bar(x=filtered_df_month.index,
                               y=filtered_df_month['СУЭ'],
                               base=0,
                               marker=dict(color='#5794a1'),
                               name='СУЭ',
                               visible=figure_user_tech_month[4])

        trace_sue_osp_bar = go.Bar(x=filtered_df_month.index,
                                   y=filtered_df_month['СУЭ ОСП'],
                                   base=0,
                                   marker=dict(color='#9b5050'),
                                   visible=figure_user_tech_month[5])

        data_tech = [trace_rtk, trace_sue, trace_sue_osp, trace_rtk_bar, trace_sue_bar, trace_sue_osp_bar]

        layout_tech = dict(
            autosize=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1),
        )

        return [{
            "data": data_tech,
            "layout": layout_tech}, {
            "data": data_tech,
            "layout": layout_tech}]


@app.callback(
    Output('site_week', 'figure'),
    Output('site_month', 'figure'),
    [Input('choice_period', 'value'),
     Input('slider_site_week', 'value'),
     Input('dropdown_site_week', 'value'),
     Input('slider_site_month', 'value'),
     Input('dropdown_site_month', 'value')
     ])
def update_figure_site(tab, selected_week_site, figure_site_type, selected_month_site, figure_site_type_month):
    site_df_upd = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
    site_df_upd.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
    site_df_upd.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    site_df_upd.set_index(site_df_upd.columns[0], inplace=True)
    site_df_upd['month'] = pd.to_datetime(site_df_upd.index)
    site_df_upd['month'] = site_df_upd['month'].dt.month
    site_df_upd['week'] = pd.to_datetime(site_df_upd.index)
    site_df_upd['week'] = site_df_upd['week'].dt.isocalendar().week

    filtered_site_df_week = site_df_upd[site_df_upd['week'] == selected_week_site]
    filtered_site_df_month = site_df_upd[site_df_upd['month'] == selected_month_site]

    if tab == 'weeks':
        figure_site_type = eval_expression(figure_site_type)

        trace_budget_bar = go.Bar(x=filtered_site_df_week.index,
                                  y=filtered_site_df_week['Электронный бюджет'],
                                  base=0,
                                  marker=dict(color='#d54062'),
                                  name='Электронный бюджет',
                                  visible=figure_site_type[0])

        trace_news_bar = go.Bar(x=filtered_site_df_week.index,
                                y=filtered_site_df_week['Новости'],
                                base=0,
                                marker=dict(color='#ffa36c'),
                                name='Новости',
                                visible=figure_site_type[1])

        trace_about_bar = go.Bar(x=filtered_site_df_week.index,
                                 y=filtered_site_df_week['О межрегиональном бухгалтерском УФК'],
                                 base=0,
                                 marker=dict(color='#ebdc87'),
                                 name='О межрегиональном бухгалтерском УФК',
                                 visible=figure_site_type[2])

        trace_other_bar = go.Bar(x=filtered_site_df_week.index,
                                 y=filtered_site_df_week['Иная деятельность'],
                                 base=0,
                                 marker=dict(color='#799351'),
                                 name='Иная деятельность',
                                 visible=figure_site_type[3])

        trace_budget_line = go.Scatter(x=filtered_site_df_week.index,
                                       y=filtered_site_df_week['Электронный бюджет'],
                                       name='Электронный бюджет',
                                       mode='lines+markers',
                                       marker=dict(size=15),
                                       line=dict(color='#d54062', width=5),
                                       visible=figure_site_type[4])

        trace_news_line = go.Scatter(x=filtered_site_df_week.index,
                                     y=filtered_site_df_week['Новости'],
                                     name='Новости',
                                     mode='lines+markers',
                                     marker=dict(size=15),
                                     line=dict(color='#ffa36c', width=5),
                                     visible=figure_site_type[5])

        trace_about_line = go.Scatter(x=filtered_site_df_week.index,
                                      y=filtered_site_df_week['О межрегиональном бухгалтерском УФК'],
                                      name='О межрегиональном бухгалтерском УФК',
                                      mode='lines+markers',
                                      marker=dict(size=15),
                                      line=dict(color='#ebdc87', width=5),
                                      visible=figure_site_type[6])
        trace_other_line = go.Scatter(x=filtered_site_df_week.index,
                                      y=filtered_site_df_week['Иная деятельность'],
                                      name='Иная деятельность',
                                      mode='lines+markers',
                                      marker=dict(size=15),
                                      line=dict(color='#799351', width=5),
                                      visible=figure_site_type[7])

        data_site = [trace_budget_bar, trace_news_bar, trace_about_bar, trace_other_bar, trace_budget_line,
                     trace_news_line, trace_about_line, trace_other_line]

        layout_site = dict(
            title='Статистика посещаний разделов сайта',
            autosize=True,
        )

        return [{
            "data": data_site,
            "layout": layout_site},
            {"data": data_site,
             "layout": layout_site}]

    elif tab == 'months':
        figure_site_type_month = eval_expression(figure_site_type_month)

        trace_budget_bar = go.Bar(x=filtered_site_df_month.index,
                                  y=filtered_site_df_month['Электронный бюджет'],
                                  base=0,
                                  marker=dict(color='#d54062'),
                                  name='Электронный бюджет',
                                  visible=figure_site_type_month[0])

        trace_news_bar = go.Bar(x=filtered_site_df_month.index,
                                y=filtered_site_df_month['Новости'],
                                base=0,
                                marker=dict(color='#ffa36c'),
                                name='Новости',
                                visible=figure_site_type_month[1])

        trace_about_bar = go.Bar(x=filtered_site_df_month.index,
                                 y=filtered_site_df_month['О межрегиональном бухгалтерском УФК'],
                                 base=0,
                                 marker=dict(color='#ebdc87'),
                                 name='О межрегиональном бухгалтерском УФК',
                                 visible=figure_site_type_month[2])

        trace_other_bar = go.Bar(x=filtered_site_df_month.index,
                                 y=filtered_site_df_month['Иная деятельность'],
                                 base=0,
                                 marker=dict(color='#799351'),
                                 name='Иная деятельность',
                                 visible=figure_site_type_month[3])

        trace_budget_line = go.Scatter(x=filtered_site_df_month.index,
                                       y=filtered_site_df_month['Электронный бюджет'],
                                       name='Электронный бюджет',
                                       mode='lines+markers',
                                       marker=dict(size=15),
                                       line=dict(color='#d54062', width=5),
                                       visible=figure_site_type_month[4])

        trace_news_line = go.Scatter(x=filtered_site_df_month.index,
                                     y=filtered_site_df_month['Новости'],
                                     name='Новости',
                                     mode='lines+markers',
                                     marker=dict(size=15),
                                     line=dict(color='#ffa36c', width=5),
                                     visible=figure_site_type_month[5])

        trace_about_line = go.Scatter(x=filtered_site_df_month.index,
                                      y=filtered_site_df_month['О межрегиональном бухгалтерском УФК'],
                                      name='О межрегиональном бухгалтерском УФК',
                                      mode='lines+markers',
                                      marker=dict(size=15),
                                      line=dict(color='#ebdc87', width=5),
                                      visible=figure_site_type_month[6])

        trace_other_line = go.Scatter(x=filtered_site_df_month.index,
                                      y=filtered_site_df_month['Иная деятельность'],
                                      name='Иная деятельность',
                                      mode='lines+markers',
                                      marker=dict(size=15),
                                      line=dict(color='#799351', width=5),
                                      visible=figure_site_type_month[7])

        data_site = [trace_budget_bar, trace_news_bar, trace_about_bar, trace_other_bar, trace_budget_line,
                     trace_news_line, trace_about_line, trace_other_line]

        layout_site = dict(
            title='Статистика посещаний разделов сайта',
            autosize=True,
        )

        return [{
            "data": data_site,
            "layout": layout_site},
            {"data": data_site,
             "layout": layout_site}]


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.109', port=8050)
