import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import date, timedelta
from LoadData import LoadEtspData, LoadSueData, EtspCountMeanTime, SueCountMeanTime, LoadInfSystemsData

current_month = date.today().month
current_day = date.today().day
current_year = date.today().year

end_day = (date.today() + timedelta(days=7)).day
end_month = (date.today() + timedelta(days=7)).month
end_year = (date.today() + timedelta(days=7)).year


def load_data():
    df_load = pd.read_excel('data.xlsx', sheet_name='Данные')
    df_load.set_index(df_load.columns[0], inplace=True)
    # df_load['month'] = pd.to_datetime(df_load.index)
    # df_load['month'] = df_load['month'].dt.month
    # df_load['year'] = pd.to_datetime(df_load.index)
    # df_load['year'] = df_load['year'].dt.year
    # df_load['day'] = pd.to_datetime(df_load.index)
    # df_load['day'] = df_load['day'].dt.day
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

etsp_df = LoadEtspData()
sue_df = LoadSueData()
inf_systems_data = LoadInfSystemsData()


# df_site = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
# df_site.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
# df_site.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
# df_site.set_index(df_site.columns[0], inplace=True)


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

fig_inf_systems = go.Figure()
for i in range(len(inf_systems_data)):
    fig_inf_systems.add_trace(go.Bar(y=inf_systems_data.columns,
                                     x=inf_systems_data.iloc[i],
                                     name=inf_systems_data.index[i],
                                     orientation='h'))
fig_inf_systems.update_layout(barmode='stack')
fig_inf_systems.update_yaxes(tickmode="linear")

# df = load_data()
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
            dcc.Tabs(id='choice_period', value='weeks', children=[
                dcc.Tab(label='Работа с пользователями', value='weeks', children=[
                    html.Br(),
                    html.Div([
                        html.Label("Выберите период: ", className='two columns'),
                        dcc.DatePickerRange(
                            id='date_user',
                            display_format='DD-MM-YYYY',
                            min_date_allowed=date(2019, 9, 1),
                            max_date_allowed=date(2020, 12, 31),
                            # initial_visible_month=date(current_year, current_month, current_day),
                            start_date=date(2020, 10, 1),
                            end_date=date(2020, 10, 10),
                            # start_date=date(current_year, current_month, current_day),
                            # end_date=date(end_year, end_month, end_day),
                            clearable=False,
                            # with_portal=True,
                            className='four columns'
                        ),
                        html.Div(id='out_date_range_user'),
                    ]),  # range_period
                    # html.Br(),
                    # html.Hr(),
                    # html.H3('Сопровождение пользователей'),
                    html.Div([
                        html.Table([
                            html.Tr([
                                html.Td([html.Label('Количество обращений'), ]),
                                html.Td(html.Label('Количество пользователей')),
                                html.Td('Среднее время решения', colSpan=2)
                            ]),
                            html.Tr([
                                html.Td(id='tasks', rowSpan=2),
                                html.Td(id='users', rowSpan=2),
                                html.Td('ETSP'),
                                html.Td('SUE')
                            ]),
                            html.Tr([
                                html.Td(id='etsp-time'),
                                html.Td(id='sue-time')
                            ]),
                            html.Tr([

                            ]),
                            html.Tr([

                            ]),
                        ], className='table1'),
                    ]),
                    html.Div([
                        dcc.Graph(id='users_figure'),
                    ], className='four columns'),  # html div user graph
                    html.Div([
                        dcc.Graph(id='support_figure'),
                    ], className='seven columns'),  # html div support graph
                ], className='h3'),  # tab user
                dcc.Tab(label='Работа информационных систем', value='months', children=[
                    html.Div([
                        dcc.Graph(id='inf_systems',
                                  figure=fig_inf_systems
                                  )

                    ], style=dict(border='1px solid #333'))

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
                        # html.Hr(),
                        # html.Br(),
                        # dcc.Dropdown(id='site_dropdown1',
                        #              className = 'dropdown',),
                        dcc.Graph(id='site_top_fig',
                                  figure=fig_site_top
                                  ),
                    ], className='six columns'),
                    # html.Div([
                    #     html.Br(),
                    #     html.Br(),
                    # ]),
                    html.Div([
                        # html.Hr(),
                        # html.Br(),
                        # dcc.Dropdown(id='site_dropdown1',
                        #              className = 'dropdown',),
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
            ], className='tab'),  # main tabs end
            html.Div(id='tabs_content')
        ])  # html.div 2
    ])  # html.div 1
])  # app layout end


@app.callback(
    Output('users_figure', 'figure'),
    Output('tasks', 'children'),
    Output('users', 'children'),
    Output('etsp-time', 'children'),
    Output('sue-time', 'children'),
    [Input('date_user', 'start_date'),
     Input('date_user', 'end_date'),
     ])
def update_figure_user(start_date_user, end_date_user):
    # etsp_df = LoadEtspData()
    # sue_df = LoadSueData()

    etsp_filtered_df = etsp_df[(etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
    sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]

    etsp_count_tasks = etsp_filtered_df['count_task'].sum()
    sue_count_tasks = sue_filtered_df['count_task'].sum()

    total_users = len(etsp_filtered_df['Затронутый пользователь'].unique()) + len(
        sue_filtered_df['Получатель услуг'].unique())

    etsp_avg_time = EtspCountMeanTime(etsp_filtered_df)
    sue_avg_time = SueCountMeanTime(sue_filtered_df)

    trace_offline_bar = go.Bar(y=[etsp_count_tasks, sue_count_tasks],
                               x=['ЕЦП', 'СУЭ'],
                               base=0,
                               marker=dict(color='crimson'))

    data_user = [trace_offline_bar]

    layout_user = dict(
        autosize=True,
        # height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1),
    )

    total_tasks = etsp_count_tasks + sue_count_tasks

    return {
               "data": data_user,
               "layout": layout_user}, total_tasks, total_users, etsp_avg_time, sue_avg_time


@app.callback(
    Output('support_figure', 'figure'),
    [Input('date_user', 'start_date'),
     Input('date_user', 'end_date'),
     ])
def update_figure_support(start_date_user, end_date_user):
    etsp_filtered_df = etsp_df[(etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
    sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]

    etsp_count_tasks = etsp_filtered_df['count_task'].sum()
    sue_count_tasks = sue_filtered_df['count_task'].sum()

    etsp_labels = ['ETSP', 'Total']
    etsp_values = [etsp_count_tasks, sue_count_tasks]
    sue_labels = ['SUE', 'Total']
    sue_values = [sue_count_tasks, etsp_count_tasks]

    if (etsp_count_tasks + sue_count_tasks) > 0:
        etsp_persent = f'{(etsp_count_tasks / (etsp_count_tasks + sue_count_tasks)):.2%}'
        sue_persent = f'{(sue_count_tasks / (etsp_count_tasks + sue_count_tasks)):.2%}'
    else:
        etsp_persent = 0
        sue_persent = 0

    etsp_colors = ['#a92b2b', '#222780']
    sue_colors = ['#37a17c', '#222780']

    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])

    fig.add_trace(go.Pie(labels=etsp_labels, values=etsp_values, name="ETSP", marker_colors=etsp_colors), 1, 1)
    fig.add_trace(go.Pie(labels=sue_labels, values=sue_values, name="SUE", marker_colors=sue_colors), 1, 2)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=etsp_persent, x=0.18, y=0.5, align='center', font_size=15, showarrow=False),
                     dict(text=sue_persent, x=0.83, y=0.5, align='center', font_size=15, showarrow=False)],
        showlegend=False)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.43', port=8000)
