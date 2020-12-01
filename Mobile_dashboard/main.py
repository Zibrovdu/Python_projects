import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

current_month = date.today().month
current_day = date.today().day
current_year = date.today().year

end_day = (date.today() + timedelta(days=7)).day
end_month = (date.today() + timedelta(days=7)).month
end_year = (date.today() + timedelta(days=7)).year


def load_data():
    df_load = pd.read_excel('data.xlsx', sheet_name='Данные')
    df_load.set_index(df_load.columns[0], inplace=True)
    return df_load


def eval_expression(input_string):
    """Эта функция полностью запрещает использование имен в eval(). (В целях безопасности)"""
    code = compile(input_string, "<string>", "eval")
    if code.co_names:
        raise NameError(f"Использование имён запрещено.")
    return eval(code, {"__builtins__": {}}, {})


external_stylesheets = ['assets/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H2('Отчет о работе Отдела сопровождения пользователей'),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            dcc.Tabs(id='choice_period', value='weeks', children=[
                dcc.Tab(label='Техническая поддержка', value='weeks', children=[
                    html.Br(),
                    html.Div([
                        html.Label("Выберите период: ", className='two columns'),
                        dcc.DatePickerRange(
                            id='date_user',
                            display_format='DD-MM-YYYY',
                            min_date_allowed=date(2019, 9, 1),
                            max_date_allowed=date(2020, 12, 31),
                            start_date=date(current_year, current_month, current_day),
                            end_date=date(end_year, end_month, end_day),
                            clearable=False,
                            with_portal=True,
                            className='four columns'
                        ),
                        html.Div(id='out_date_range_user'),
                    ]),
                    html.Br(),
                    html.Hr(),
                    html.H3('Сопровождение пользователей'),
                    html.Div([
                        html.Hr(),
                        html.Br(),
                        html.Br(),
                        dcc.Dropdown(id='user_dropdown',
                                     options=[
                                         dict(label='Линейный график', value='[True, True, False, False]'),
                                         dict(label='Столбчатая диаграмма', value='[False, False, True, True]')],
                                     value='[True, True, False, False]',
                                     clearable=False,
                                     searchable=False,
                                     style=dict(width='250px', margin='30px, 0px')),
                        dcc.Graph(id='users_figure'),
                    ]),
                    html.Hr(),
                    html.H3('Техническая поддержка'),
                    html.Hr(),
                    html.Div([
                        html.Br(),
                        html.Br(),
                        dcc.Dropdown(id='tech_dropdown',
                                     options=[
                                         dict(label='Линейный график', value='[True, True, True, False, False, '
                                                                             'False]'),
                                         dict(label='Столбчатая диаграмма', value='[False, False, False, True, '
                                                                                  'True, True]')],
                                     value='[True, True, True, False, False, False]',
                                     clearable=False,
                                     searchable=False,
                                     style=dict(width='250px', margin='30px, 0px')),
                        dcc.Graph(id='tech_figure'),
                    ]),
                ], className='h3'),
                dcc.Tab(label='Работа информационных систем', value='months', children=[

                ]),
                dcc.Tab(label='Статистика сайта', value='s', children=[
                    html.Br(),
                    html.Div([
                        html.Label("Выберите период: ", className='two columns'),
                        dcc.DatePickerRange(
                            id='date_site',
                            display_format='DD-MM-YYYY',
                            min_date_allowed=date(2019, 9, 1),
                            max_date_allowed=date(2020, 12, 31),
                            start_date=date(current_year, current_month, current_day),
                            end_date=date(end_year, end_month, end_day),
                            clearable=False,
                            with_portal=True,
                            className='four columns'
                        ),
                        html.Div(id='out_date_range_site'),
                    ]),
                    html.Br(),
                    html.Hr(),
                    html.H3('Статистика посещаний разделов сайта'),
                    html.Div([
                        html.Hr(),
                        html.Br(),
                        html.Br(),
                        dcc.Dropdown(id='site_dropdown',
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
                        dcc.Graph(id='site_figure'),
                    ]),

                ]),
            ]),
            html.Div(id='tabs_content')
        ])
    ])
])


@app.callback(
    Output('users_figure', 'figure'),
    [Input('user_dropdown', 'value'),
     Input('date_user', 'start_date'),
     Input('date_user', 'end_date'),
     ])
def update_figure_user(figure_user_type, start_date_user, end_date_user):
    df_user = load_data()
    filtered_df = df_user[(df_user.index >= start_date_user) & (df_user.index <= end_date_user)]

    figure_user_type = eval_expression(figure_user_type)

    trace_office = go.Scatter(x=filtered_df.index,
                              y=filtered_df['Сопровождение пользователя в офисе'],
                              name='работа в офисе',
                              mode='lines+markers',
                              marker=dict(size=15),
                              line=dict(color='crimson', width=5),
                              visible=figure_user_type[0])
    trace_online = go.Scatter(x=filtered_df.index,
                              y=filtered_df['Сопровождение пользователя на удаленной работе'],
                              name='удаленная работа',
                              mode='lines+markers',
                              marker=dict(size=15),
                              line=dict(color='lightslategrey', width=5),
                              visible=figure_user_type[1])
    trace_offline_bar = go.Bar(x=filtered_df.index,
                               y=filtered_df['Сопровождение пользователя в офисе'],
                               base=0,
                               marker=dict(color='crimson'),
                               name='работа в офисе',
                               visible=figure_user_type[2])
    trace_online_bar = go.Bar(x=filtered_df.index,
                              y=filtered_df['Сопровождение пользователя на удаленной работе'],
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

    return {
        "data": data_user,
        "layout": layout_user}


@app.callback(
    Output('tech_figure', 'figure'),
    [Input('tech_dropdown', 'value'),
     Input('date_user', 'start_date'),
     Input('date_user', 'end_date'),
     ])
def update_figure_user(figure_tech_type, start_date_tech, end_date_tech):
    df_tech = load_data()
    filtered_df_tech = df_tech[(df_tech.index >= start_date_tech) & (df_tech.index <= end_date_tech)]

    figure_tech_type = eval_expression(figure_tech_type)

    trace_rtk = go.Scatter(x=filtered_df_tech.index,
                           y=filtered_df_tech['РТК'],
                           name='РТК',
                           mode='lines+markers',
                           marker=dict(size=15),
                           line=dict(color='#67b18d', width=5),
                           visible=figure_tech_type[0])

    trace_sue = go.Scatter(x=filtered_df_tech.index,
                           y=filtered_df_tech['СУЭ'],
                           name='СУЭ',
                           mode='lines+markers',
                           marker=dict(size=15),
                           line=dict(color='#5794a1', width=5),
                           visible=figure_tech_type[1])

    trace_sue_osp = go.Scatter(x=filtered_df_tech.index,
                               y=filtered_df_tech['СУЭ ОСП'],
                               name='СУЭ ОСП',
                               mode='lines+markers',
                               marker=dict(size=15),
                               line=dict(color='#9b5050', width=5),
                               visible=figure_tech_type[2])

    trace_rtk_bar = go.Bar(x=filtered_df_tech.index,
                           y=filtered_df_tech['РТК'],
                           base=0,
                           marker=dict(color='#67b18d'),
                           name='РТК',
                           visible=figure_tech_type[3])

    trace_sue_bar = go.Bar(x=filtered_df_tech.index,
                           y=filtered_df_tech['СУЭ'],
                           base=0,
                           marker=dict(color='#5794a1'),
                           name='СУЭ',
                           visible=figure_tech_type[4])

    trace_sue_osp_bar = go.Bar(x=filtered_df_tech.index,
                               y=filtered_df_tech['СУЭ ОСП'],
                               base=0,
                               marker=dict(color='#9b5050'),
                               name='СУЭ ОСП',
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

    return {
        "data": data_tech,
        "layout": layout_tech}


@app.callback(
    Output('site_figure', 'figure'),
    [Input('site_dropdown', 'value'),
     Input('date_site', 'start_date'),
     Input('date_site', 'end_date'),
     ])
def update_figure_user(figure_site_type, start_date_site, end_date_site):
    df_site = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
    df_site.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
    df_site.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    df_site.set_index(df_site.columns[0], inplace=True)

    filtered_df_site = df_site[(df_site.index >= start_date_site) & (df_site.index <= end_date_site)]

    figure_site_type = eval_expression(figure_site_type)

    trace_budget_bar = go.Bar(x=filtered_df_site.index,
                              y=filtered_df_site['Электронный бюджет'],
                              base=0,
                              marker=dict(color='#d54062'),
                              name='Электронный бюджет',
                              visible=figure_site_type[0])

    trace_news_bar = go.Bar(x=filtered_df_site.index,
                            y=filtered_df_site['Новости'],
                            base=0,
                            marker=dict(color='#ffa36c'),
                            name='Новости',
                            visible=figure_site_type[1])

    trace_about_bar = go.Bar(x=filtered_df_site.index,
                             y=filtered_df_site['О межрегиональном бухгалтерском УФК'],
                             base=0,
                             marker=dict(color='#ebdc87'),
                             name='О межрегиональном бухгалтерском УФК',
                             visible=figure_site_type[2])

    trace_other_bar = go.Bar(x=filtered_df_site.index,
                             y=filtered_df_site['Иная деятельность'],
                             base=0,
                             marker=dict(color='#799351'),
                             name='Иная деятельность',
                             visible=figure_site_type[3])

    trace_budget_line = go.Scatter(x=filtered_df_site.index,
                                   y=filtered_df_site['Электронный бюджет'],
                                   name='Электронный бюджет',
                                   mode='lines+markers',
                                   marker=dict(size=15),
                                   line=dict(color='#d54062', width=5),
                                   visible=figure_site_type[4])

    trace_news_line = go.Scatter(x=filtered_df_site.index,
                                 y=filtered_df_site['Новости'],
                                 name='Новости',
                                 mode='lines+markers',
                                 marker=dict(size=15),
                                 line=dict(color='#ffa36c', width=5),
                                 visible=figure_site_type[5])

    trace_about_line = go.Scatter(x=filtered_df_site.index,
                                  y=filtered_df_site['О межрегиональном бухгалтерском УФК'],
                                  name='О межрегиональном бухгалтерском УФК',
                                  mode='lines+markers',
                                  marker=dict(size=15),
                                  line=dict(color='#ebdc87', width=5),
                                  visible=figure_site_type[6])
    trace_other_line = go.Scatter(x=filtered_df_site.index,
                                  y=filtered_df_site['Иная деятельность'],
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

    return {
        "data": data_site,
        "layout": layout_site}


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.43', port=8060)
