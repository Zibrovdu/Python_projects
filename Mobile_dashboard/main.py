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


def load_data_site():
    df = pd.read_excel('site.xlsx', skiprows=6)
    df['Страница входа, ур. 4'] = df['Страница входа, ур. 4'].fillna('')
    df2 = df[df['Страница входа, ур. 4'].str.contains('molodezhnyy-sovet')][['Страница входа, ур. 4', 'Визиты',
                                                                             'Посетители', 'Просмотры',
                                                                             'Доля новых посетителей']]
    df2 = pd.DataFrame(df2.groupby(['Страница входа, ур. 4'], as_index=False)[['Визиты', 'Посетители', 'Просмотры',
                                                                               'Доля новых посетителей']].sum())
    df2 = df2.rename(columns={'Страница входа, ур. 4': 'Страница входа, ур. 2'})
    df = pd.DataFrame(df.groupby(['Страница входа, ур. 2'], as_index=False)[
                          ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']].sum())
    df.loc[13, 'Страница входа, ур. 2'] = 'https://mbufk.roskazna.gov.ru/'
    df = df.append(df2).reset_index()
    df.drop('index', axis=1, inplace=True)
    df.loc[8, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']] = df.loc[8, ['Визиты', 'Посетители',
                                                                                            'Просмотры',
                                                                                            'Доля новых посетителей']] - \
                                                                                 df.loc[14, ['Визиты', 'Посетители',
                                                                                             'Просмотры',
                                                                                             'Доля новых посетителей']]
    df2 = pd.read_excel('site.xlsx', sheet_name='перевод', header=None)
    df['Название'] = ''
    for num in range(len(df2)):
        mask = df['Страница входа, ур. 2'].isin(df2.iloc[num])
        df.loc[mask, 'Название'] = df2.iloc[num][1]
    return df


site_top_df = load_data_site()
site_top_df.sort_values('Визиты', inplace=True)
site_label = site_top_df.sort_values('Название').reset_index().drop('index', axis=1)

site_1_df = pd.read_excel('site.xlsx', skiprows=6, nrows=1, usecols='A,F,G,H,N')

site_label1 = site_top_df.sort_values('Посетители', ascending=False).reset_index().drop('index', axis=1)


def load_data_eb():
    df = pd.read_excel('site.xlsx', skiprows=6)
    df = df[df['Страница входа, ур. 2'] == 'https://mbufk.roskazna.gov.ru/elektronnyy-byudzhet/']
    df_eb = df.groupby('Страница входа, ур. 3', as_index=False)['Глубина просмотра'].sum()
    df4 = pd.read_excel('site.xlsx', sheet_name='перевод', skiprows=15, header=None)
    df_eb['site_page'] = ''
    for num in range(len(df4)):
        mask = df_eb['Страница входа, ур. 3'].isin(df4.iloc[num])
        df_eb.loc[mask, 'site_page'] = df4.iloc[num][1]
    return df_eb


el_b_df = load_data_eb()
fig_site_top3 = go.Figure(data=[go.Pie(labels=el_b_df['site_page'], values=el_b_df['Глубина просмотра'], hole=.3)])
fig_site_top3.update_layout(title_text="Глубина просмотра раздела Электронный бюджет", autosize=True, piecolorway=[
    '#26205b', '#3257af', '#c8abd5', '#f9c5d8', '#b83e74', '#8d0837', '#9456ef'])


def eval_expression(input_string):
    """Эта функция полностью запрещает использование имен в eval(). (В целях безопасности)"""
    code = compile(input_string, "<string>", "eval")
    if code.co_names:
        raise NameError(f"Использование имён запрещено.")
    return eval(code, {"__builtins__": {}}, {})


fig_site_top = go.Figure([go.Bar(
    x=site_top_df['Визиты'],
    y=site_top_df['Название'],
    orientation='h',
    text=site_top_df['Визиты'])])
fig_site_top.update_traces(textposition='outside')
fig_site_top.update_layout(
    title_text="Количество визитов")

labels = list(site_label1['Название'].head(5))
labels.append("Остальные")
values = list(site_label1['Посетители'].head(5))
values.append(site_label1.loc[5:14]['Посетители'].sum())

fig_site_top2 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
fig_site_top2.update_layout(
    title_text="Количество посетителей")

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
                            # initial_visible_month=date(current_year, current_month, current_day),
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
                    ]),  # html div user graph
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
                    ]),  # html div tech graph
                ], className='h3'),  # tab user
                dcc.Tab(label='Работа информационных систем', value='months', children=[

                ]),  # tab tech
                dcc.Tab(label='Статистика сайта', value='s', children=[
                    html.Br(),
                    html.Div([
                        html.Table([
                            html.Tr([
                                html.Td([
                                    html.Label('Суммарное количество визитов за год'),
                                ]),
                                html.Td([
                                    html.Label(site_1_df['Визиты'][0]),
                                ]),
                            ]),
                            html.Tr([
                                html.Td(html.Label('Количество уникальных посетителей за год')),
                                html.Td(html.Label(site_1_df['Посетители'][0])),
                            ]),
                        ], className='table'),
                    ]),
                    html.Br(),
                    html.Hr(),
                    html.H3('Рейтинг посещаемости разделов сайта за год'),
                    html.Div([
                        dcc.Graph(id='site_top_fig',
                                  figure=fig_site_top
                                  ),
                    ], className='six columns'),
                    html.Div([
                        dcc.Graph(id='site_top_fig2',
                                  figure=fig_site_top2
                                  ),
                    ], className='five columns'),
                    html.H3('Рейтинг посещаемости разделов сайта за год'),
                    html.Div([
                        dcc.Graph(id='site_top_fig3',
                                  figure=fig_site_top3
                                  ),
                    ], className='six columns'),
                ]),  # tab site
            ]),  # main tabs end
            html.Div(id='tabs_content')
        ])  # html.div 2
    ])  # html.div 1
])  # app layout end


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
def update_figure_tech(figure_tech_type, start_date_tech, end_date_tech):

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


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.43', port=8050)
