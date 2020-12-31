import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from LoadData import LoadEtspData, LoadSueData, CountMeanTime, LoadInfSystemsData, LoadOspData

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
    df.loc[8, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']] = \
        df.loc[8, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']] - \
        df.loc[14, ['Визиты', 'Посетители', 'Просмотры', 'Доля новых посетителей']]

    df2 = pd.read_excel('site.xlsx', sheet_name='перевод', header=None)
    df['Название'] = ''
    for num in range(len(df2)):
        mask = df['Страница входа, ур. 2'].isin(df2.iloc[num])
        df.loc[mask, 'Название'] = df2.iloc[num][1]
    df3 = df[(df['Название'] == 'О Межрегиональном бухгалтерском УФК') | (df['Название'] == 'Новости') |
             (df['Название'] == 'Документы') | (df['Название'] == 'Электронный бюджет') |
             (df['Название'] == 'Иная деятельность') | (df['Название'] == 'Прием обращений')]
    return df3


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
fig_site_top3.update_layout(title_text="Глубина просмотра раздела Электронный бюджет",
                            autosize=True,
                            piecolorway=['#26205b', '#3257af', '#c8abd5', '#f9c5d8', '#b83e74', '#8d0837', '#9456ef'],
                            paper_bgcolor='#ebecf1',
                            plot_bgcolor='#ebecf1')

etsp_df = LoadEtspData()
top_user_etsp = pd.DataFrame(etsp_df.groupby('Имя затронутого пользователя')['count_task'].sum()
                             .sort_values(ascending=False).head()
                             .reset_index()).rename(columns={'Имя затронутого пользователя': 'Пользователь',
                                                             'count_task': 'Обращения'})
sue_df = LoadSueData()
top_user_sue = pd.DataFrame(sue_df.groupby('user')['count_task'].sum()
                            .sort_values(ascending=False).head()
                            .reset_index()).rename(
    columns={'user': 'Пользователь', 'count_task': 'Обращения'})
osp_df = LoadOspData()
inf_systems_data = LoadInfSystemsData()

sue_avaria_df = sue_df[(sue_df.status == 'Проблема') | (sue_df.status == 'Массовый инцидент')]
sue_avaria_df.columns = ['Дата обращения', 'Тип', 'Номер', 'Описание', 'Плановое время', 'Фактическое время',
                         'Пользователь', 'timedelta', 'Отдел', 'month_open', 'month_solved', 'count_task',
                         'Дата', 'finish_date']


# print(sue_avaria_df)


# df_site = pd.read_excel('data.xlsx', sheet_name='Данные по сайту', skiprows=5)
# df_site.drop(['Неделя 1', 'Unnamed: 6'], axis=1, inplace=True)
# df_site.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
# df_site.set_index(df_site.columns[0], inplace=True)

# def eval_expression(input_string):
#
#     """Эта функция полностью запрещает использование имен в eval(). (В целях безопасности)"""
#     code = compile(input_string, "<string>", "eval")
#     if code.co_names:
#         raise NameError(f"Использование имён запрещено.")
#     return eval(code, {"__builtins__": {}}, {})


colors_site_top = ['#003b32', '#40817a', '#afbaa3', '#d0d0b8', '#037c87', '#7cbdc9']

fig_site_top = go.Figure([go.Bar(x=site_top_df['Визиты'],
                                 y=site_top_df['Название'],
                                 orientation='h',
                                 marker_color=colors_site_top,
                                 text=site_top_df['Визиты'])])
fig_site_top.update_traces(textposition='auto')
fig_site_top.update_layout(title_text="Количество визитов по разделам сайта", paper_bgcolor='#ebecf1',
                           plot_bgcolor='#ebecf1')

labels = list(site_label1['Название'].head(5))
labels.append("Остальные")
values = list(site_label1['Посетители'].head(5))
values.append(site_label1.loc[5:14]['Посетители'].sum())

colors_site = ['#ba83c4', '#fca3b5', '#b1d1ed', '#fcf3b5', '#efc67c', '#82bcc7']
fig_site_top2 = go.Figure(data=[go.Pie(labels=labels,
                                       values=values,
                                       marker_colors=colors_site,
                                       hole=.2)])

fig_site_top2.update_layout(title_text="Количество посетителей", paper_bgcolor='#ebecf1', plot_bgcolor='#ebecf1')

external_stylesheets = ['assets/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

tab_selected_style = dict(backgroundColor='#ebecf1', fontWeight='bold')

d_month = [{'label': 'Январь', 'value': '1'},
           {'label': 'Февраль', 'value': '2'},
           {'label': 'Март', 'value': '3'},
           {'label': 'Апрель', 'value': '4'},
           {'label': 'Май', 'value': '5'},
           {'label': 'Июнь', 'value': '6'},
           {'label': 'Июль', 'value': '7'},
           {'label': 'Август', 'value': '8'},
           {'label': 'Сентябрь', 'value': '9'},
           {'label': 'Октябрь', 'value': '10'},
           {'label': 'Ноябрь', 'value': '11'},
           {'label': 'Декабрь', 'value': '12'}]

app.layout = html.Div([
    html.Div([
        # html.H1("Межрегиональное бухгалтерское УФК"),
        html.H2('Отдел сопровождения пользователей'),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            dcc.Tabs(id='choice_period', value='weeks', children=[
                dcc.Tab(label='Работа с пользователями', value='weeks', children=[
                    # html.Br(),
                    # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    # html.Div([html.Label("Выберите период: ")], className='slabel_block'),
                    # html.Div([dcc.DatePickerRange(id='date_user',
                    #                               display_format='DD-MM-YYYY',
                    #                               min_date_allowed=date(2019, 9, 1),
                    #                               max_date_allowed=date(2020, 12, 31),
                    #                               # initial_visible_month=date(current_year, current_month,
                    #                               # current_day),
                    #                               start_date=date(2020, 12, 10),
                    #                               end_date=date(2020, 12, 18),
                    #                               # start_date=date(current_year, current_month, current_day),
                    #                               # end_date=date(end_year, end_month, end_day),
                    #                               clearable=False
                    #                               # with_portal=True,
                    #                               ),
                    #           ], className='s_line_block', style=dict(border='1px solid black')),  # range_period
                    # html.Div([daq.ToggleSwitch(id='my-toggle-switch',
                    #                            value=False,
                    #                            label='',
                    #                            labelPosition='bottom'
                    #                            # style={'margin': '0 auto'}
                    #                            ),
                    #           ], className='.button_block', style=dict(border='1px solid black')),
                    # html.Div([dcc.Dropdown(id='month_choice',
                    #                        options=d_month,
                    #                        searchable=False,
                    #                        clearable=False,
                    #                        value=current_month,
                    #                        style=dict(width='100%'),
                    #                        disabled=False
                    #                        ),
                    #           ], className='s_line_block', style=dict(width='15%', margin='0 auto',  border='1px solid black')),
                    # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    html.Br(),
                    html.Div([html.Label("Выберите период: ")], className='bblock',
                             style=dict(width='180px')),
                    html.Div([dcc.DatePickerRange(id='date_user',
                                                  display_format='DD-MM-YYYY',
                                                  min_date_allowed=date(2019, 9, 1),
                                                  max_date_allowed=date(2020, 12, 31),
                                                  # initial_visible_month=date(current_year, current_month,
                                                  # current_day),
                                                  start_date=date(2020, 12, 10),
                                                  end_date=date(2020, 12, 18),
                                                  # start_date=date(current_year, current_month, current_day),
                                                  # end_date=date(end_year, end_month, end_day),
                                                  clearable=False
                                                  # with_portal=True,
                                                  ),
                              ], className='bblock', style=dict(width='290px')),
                    html.Div([daq.ToggleSwitch(id='my-toggle-switch',
                                               value=False,
                                               color='#1959d1',
                                               size=70
                                               ),
                              ], className='bblock', style=dict(width='160px')),
                    html.Div([dcc.Dropdown(id='month_choice',
                                           options=d_month,
                                           searchable=False,
                                           clearable=False,
                                           value=current_month,
                                           style=dict(width='100%', heigth='45px'),
                                           disabled=False
                                           ),
                              ], className='bblock', style=dict(width='140px')),

                    html.Div([
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                        html.Div([html.Table([
                            html.Tr([
                                html.Td([html.Label('Количество обращений'), ]),
                                html.Td(html.Label('Количество пользователей')),
                                html.Td('Среднее время решения', colSpan=3)
                            ]),
                            html.Tr([
                                html.Td(id='tasks', rowSpan=2, style={'fontSize': '2em'}),
                                html.Td(id='users', rowSpan=2, style={'font-size': '2.2em'}),
                                html.Td('ЕЦП'),
                                html.Td('СУЭ'),
                                html.Td('ОСП')
                            ]),
                            html.Tr([
                                html.Td(id='etsp-time'),
                                html.Td(id='sue-time'),
                                html.Td(id='osp-time')
                            ]),
                            html.Tr([

                            ]),
                            html.Tr([

                            ]),
                        ])], className='line_block', style=dict(width='60%')),  # table_1
                        html.Div([html.Label('Аварийные инциденты'),
                                  dash_table.DataTable(id='sue_avaria',
                                                       columns=[{"name": i, "id": i} for i in sue_avaria_df.columns if
                                                                i == 'Тип' or i == 'Номер' or
                                                                i == 'Описание' or i == 'Дата'],
                                                       data=sue_avaria_df.to_dict('records'),
                                                       sort_action="native",
                                                       style_table={'height': '150px', 'overflowY': 'auto'},
                                                       fixed_rows={'headers': True},
                                                       style_as_list_view=True,
                                                       cell_selectable=False,
                                                       style_data=dict(width='20%'),
                                                       css=[{
                                                           'selector': '.dash-spreadsheet td div',
                                                           'rule': '''
                                                                line-height: 10px;
                                                                max-height: 20px; min-height: 20px; height: 20px;
                                                                display: block;
                                                                overflow-y: hidden;
                                                           '''
                                                       }],
                                                       tooltip_data=[{
                                                           column: {'value': str(value), 'type': 'markdown'}
                                                           for column, value in row.items()
                                                       } for row in sue_avaria_df.to_dict('records')],
                                                       tooltip_duration=None,
                                                       style_cell=dict(textAlign='center',
                                                                       overflow='hidden',
                                                                       textOverflow='ellipsis',
                                                                       maxWidth=0))], className='line_block', style=dict(width='32%')),
                        # avariynie incidenti table
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    ]),
                    html.Hr(),
                    html.Div([
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                        html.Div([dcc.Graph(id='users_figure')], className='line_block', style=dict(width='46%')),  # html div user graph
                        html.Div([dcc.Graph(id='support_figure')], className='line_block', style=dict(width='46%')),  # html div support graph
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    ]),
                    html.Br(),
                    html.Div([html.H3('ТОП-5 пользователей направивших обращения (по техподдержкам)')],
                             style={'color': '#222780', 'font-type': 'bold'}),
                    html.Div([
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                        html.Div([html.H4('ЕЦП')], className='line_block', style=dict(width='46%')),  # html div
                        html.Div([html.H4('СУЭ')], className='line_block', style=dict(width='46%')),  # html div
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    ]),
                    html.Div([
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                        html.Div([
                            dash_table.DataTable(id='table_top_etsp',
                                                 columns=[{"name": i, "id": i} for i in top_user_etsp.columns],
                                                 # data=top_user_etsp.to_dict('records'),
                                                 sort_action="native",
                                                 style_as_list_view=True,
                                                 cell_selectable=False,
                                                 style_data={'width': '50px', 'font-size': ' 1.3em'},
                                                 style_cell=dict(textAlign='center'),
                                                 style_cell_conditional=[
                                                     {'if': {'column_id': 'Пользователь'},
                                                      'textAlign': 'left'}]
                                                 )], className='line_block', style=dict(width='46%')),
                        html.Div([
                            dash_table.DataTable(id='table_top_sue',
                                                 columns=[{"name": i, "id": i} for i in top_user_sue.columns],
                                                 # data=top_user_sue.to_dict('records'),
                                                 sort_action="native",
                                                 style_as_list_view=True,
                                                 cell_selectable=False,
                                                 style_data={'width': '50px', 'font-size': ' 1.3em'},
                                                 style_cell=dict(textAlign='center'),
                                                 style_cell_conditional=[
                                                     {'if': {'column_id': 'Пользователь'},
                                                      'textAlign': 'left'}]
                                                 )], className='line_block', style=dict(width='46%')),
                        # html div
                        # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    ]),
                ], selected_style=tab_selected_style),  # tab user
                dcc.Tab(label='Информационные системы', value='months', children=[
                    html.Br(),
                    # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    html.Div([
                        html.Table([
                            html.Tr([
                                html.Td([html.Label('Подключено сотрудников МБУ ФК к ГИИС "Электронный бюджет"')]),
                                html.Td([html.Label('Сформировано заявок:')], colSpan=2)
                            ]),
                            html.Tr([
                                html.Td([daq.LEDDisplay(id='total_tasks', value=254, color='#222780',
                                                        backgroundColor='#e8edff', )], rowSpan=2),
                                html.Td([html.Label('на подключение»')]),
                                html.Td([html.Label('на лишение полномочий')])
                            ]),
                            html.Tr([
                                html.Td([daq.LEDDisplay(id='allow_perm', value=0000, color='#28df99',
                                                        backgroundColor='#e8edff', size=20)]),
                                html.Td([daq.LEDDisplay(id='denny_perm', value=0000, color='#ec0101',
                                                        backgroundColor='#e8edff', size=20)])
                            ])
                        ], className='table_budget')
                    ], style=dict(height='165px')),
                    html.Div([
                        daq.BooleanSwitch(
                            id='leg_show',
                            label="Легенда",
                            labelPosition="top",
                            color='#1959d1',
                            on=False
                        ),
                    ], style=dict(width='15%')),
                    # html.Div([], style=dict(width='100%', height='1px', clear='both', float='left')),
                    html.Div([
                        # html.P("Показать/скрыть легенду"),

                        # dcc.RadioItems(id='leg_show',
                        #                options=[{'label': 'Показать', 'value': 1},
                        #                         {'label': 'Скрыть', 'value': 0}],
                        #                value=0,
                        #                labelStyle={'display': 'inline-block'}
                        #                ),
                        dcc.Graph(id='inf_systems')
                    ], style=dict(background='#ebecf1'))
                ], selected_style=tab_selected_style),  # tab tech
                dcc.Tab(label='Сайт', value='s', children=[
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
                    html.Div([dcc.Graph(id='site_top_fig', figure=fig_site_top)]),
                    html.Div([dcc.Graph(id='site_top_fig2', figure=fig_site_top2)]),
                    html.Div([dcc.Graph(id='site_top_fig3', figure=fig_site_top3)]),
                ], selected_style=tab_selected_style),  # tab site
            ], colors=dict(border='#ebecf1', primary='#222780', background='#33ccff')),  # main tabs end
            html.Div(id='tabs_content')
        ])  # html.div 2
    ], style=dict(background='#ebecf1'))  # html.div 1
])  # app layout end


# @app.callback(
#     Output('users_figure', 'figure'),
#     Output('tasks', 'children'),
#     Output('users', 'children'),
#     Output('etsp-time', 'children'),
#     Output('sue-time', 'children'),
#     Output('osp-time', 'children'),
#     [Input('date_user', 'start_date'),
#      Input('date_user', 'end_date'),
#      ])
# def update_figure_user(start_date_user, end_date_user):
#     # etsp_df = LoadEtspData()
#     # sue_df = LoadSueData()
#     # print(start_date_user, type(start_date_user))
#     # print(end_date_user)
#
#     etsp_filtered_df = etsp_df[(etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
#     sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]
#     osp_filtered_df = osp_df[(osp_df['start_date'] >= start_date_user) & (osp_df['start_date'] <= end_date_user)]
#
#     etsp_count_tasks = etsp_filtered_df['count_task'].sum()
#     sue_count_tasks = sue_filtered_df['count_task'].sum()
#     osp_count_tasks = osp_filtered_df['count_task'].sum()
#
#     total_users = len(etsp_filtered_df['Имя затронутого пользователя'].unique()) + len(
#         sue_filtered_df['user'].unique()) + len(osp_filtered_df['Пользователь'].unique())
#
#     etsp_avg_time = CountMeanTime(etsp_filtered_df)
#     sue_avg_time = CountMeanTime(sue_filtered_df)
#     osp_avg_time = CountMeanTime(osp_filtered_df)
#
#     fig_support = go.Figure(go.Bar(y=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
#                                    x=['ЕЦП', 'СУЭ', 'ОСП'],
#                                    base=0,
#                                    marker=dict(color=['#a92b2b', '#37a17c', '#a2d5f2']),
#                                    text=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
#                                    textposition='auto'))
#     fig_support.update_layout(autosize=True,
#                               # height=700,
#                               legend=dict(
#                                   orientation="h",
#                                   yanchor="bottom",
#                                   y=0.2,
#                                   xanchor="right",
#                                   x=0.5),
#                               paper_bgcolor='#ebecf1',
#                               plot_bgcolor='#ebecf1'
#                               )
#     fig_support.update_xaxes(ticks="inside",
#                              tickson="boundaries")
#
#     total_tasks = etsp_count_tasks + sue_count_tasks + osp_count_tasks
#
#     return fig_support, total_tasks, total_users, etsp_avg_time, sue_avg_time, osp_avg_time

# @app.callback(
#     Output('support_figure', 'figure'),
#     [Input('date_user', 'start_date'),
#      Input('date_user', 'end_date'),
#      ])
# def update_figure_support(start_date_user, end_date_user):
#     etsp_filtered_df = etsp_df[(etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
#     sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]
#     osp_filtered_df = osp_df[(osp_df['start_date'] >= start_date_user) & (osp_df['start_date'] <= end_date_user)]

# etsp_count_tasks = etsp_filtered_df['count_task'].sum()
# sue_count_tasks = sue_filtered_df['count_task'].sum()
# osp_count_tasks = osp_filtered_df['count_task'].sum()
#
# etsp_labels = ['ETSP', 'Total']
# etsp_values = [etsp_count_tasks, sue_count_tasks + osp_count_tasks]
# sue_labels = ['SUE', 'Total']
# sue_values = [sue_count_tasks, etsp_count_tasks + osp_count_tasks]
# osp_labels = ['SUE', 'Total']
# osp_values = [osp_count_tasks, etsp_count_tasks + sue_count_tasks]

# if (etsp_count_tasks + sue_count_tasks + osp_count_tasks) > 0:
#     etsp_persent = f'{(etsp_count_tasks / (etsp_count_tasks + sue_count_tasks + osp_count_tasks)):.2%}'
#     sue_persent = f'{(sue_count_tasks / (etsp_count_tasks + sue_count_tasks + osp_count_tasks)):.2%}'
#     osp_persent = f'{(osp_count_tasks / (etsp_count_tasks + sue_count_tasks + osp_count_tasks)):.2%}'
# else:
#     etsp_persent = 0
#     sue_persent = 0
#     osp_persent = 0

# etsp_colors = ['#a92b2b', '#222780']
# sue_colors = ['#37a17c', '#222780']
# osp_colors = ['#a2d5f2', '#222780']
#
# fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]])
#
# fig.add_trace(go.Pie(labels=etsp_labels, values=etsp_values, name="ЕЦП", marker_colors=etsp_colors), 1, 1)
# fig.add_trace(go.Pie(labels=sue_labels, values=sue_values, name="СУЭ", marker_colors=sue_colors), 1, 2)
# fig.add_trace(go.Pie(labels=osp_labels, values=osp_values, name="ОСП", marker_colors=osp_colors), 1, 3)

# Use `hole` to create a donut-like pie chart
# labels_figure_support = ["ЕЦП", "СУЭ", "ОСП"]
# values_figure_support = [etsp_filtered_df['count_task'].sum(), sue_filtered_df['count_task'].sum(),
#                          osp_filtered_df['count_task'].sum()]
# colors = ['#a92b2b', '#37a17c', '#a2d5f2']
#
# fig = go.Figure(go.Pie(labels=labels_figure_support, values=values_figure_support, marker_colors=colors))
# fig.update_traces(hoverinfo="label+percent+name")
#
# fig.update_layout(
#     paper_bgcolor='#ebecf1',
#     # Add annotations in the center of the donut pies.
#     # annotations=[dict(text=etsp_persent, x=0.11, y=0.5, align='center', showarrow=False),
#     #              dict(text=sue_persent, x=0.50, y=0.5, align='center', showarrow=False),
#     #              dict(text=osp_persent, x=0.89, y=0.5, align='center', showarrow=False)],
#     showlegend=True)

# return fig


# @app.callback(
#     Output('sue_avaria', 'data'),
#     [Input('date_user', 'start_date'),
#      Input('date_user', 'end_date'),
#      ])
# def update_table_avaria(start_date_user, end_date_user):
#     sue_avaria_filtered_df = sue_avaria_df[(sue_avaria_df['Дата обращения'] >= start_date_user) &
#                                            (sue_avaria_df['Дата обращения'] <= end_date_user)]
#
#     if len(sue_avaria_filtered_df) > 0:
#         return sue_avaria_filtered_df.to_dict('records')
#     else:
#         return [{'Дата': '-', 'Тип': 'Аварийных инциндентов нет', 'Номер': '-', 'Описание': '-',
#                  'Плановое время': '-', 'Фактическое время': '-', 'Пользователь': '-', 'timedelta': '-', 'Отдел': '-',
#                  'month_open': '-', 'month_solved': '-', 'count_task': '-', 'Дата обращения': '-',
#                  'finish_date': '-'}]


@app.callback(
    Output("inf_systems", "figure"),
    [Input("leg_show", "on")])
def modify_legend(on):
    fig_inf_systems = go.Figure()
    for i in range(len(inf_systems_data)):
        fig_inf_systems.add_trace(go.Bar(y=inf_systems_data.columns,
                                         x=inf_systems_data.iloc[i],
                                         name=inf_systems_data.index[i],
                                         orientation='h',
                                         text=inf_systems_data.iloc[i],
                                         textposition='inside'))
    fig_inf_systems.update_layout(barmode='stack',
                                  height=1000,
                                  # legend_font_size=10,
                                  # legend_itemwidth=40,
                                  legend_xanchor='right',
                                  paper_bgcolor='#ebecf1',
                                  plot_bgcolor='#ebecf1',
                                  showlegend=on)
    fig_inf_systems.update_yaxes(tickmode="linear")

    return fig_inf_systems


# @app.callback(
#     Output('table_top_etsp', 'data'),
#     [Input('date_user', 'start_date'),
#      Input('date_user', 'end_date'),
#      ])
# def update_table_top_etsp(start_date_user, end_date_user):
#     etsp_filtered_df = etsp_df[(etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
#     top_user_etsp_filtered_df = pd.DataFrame(
#         etsp_filtered_df.groupby('Имя затронутого пользователя')['count_task'].sum()
#             .sort_values(ascending=False).head()
#             .reset_index()).rename(columns={'Имя затронутого пользователя': 'Пользователь',
#                                             'count_task': 'Обращения'})
#     return top_user_etsp_filtered_df.to_dict('records')


# @app.callback(
#     Output('table_top_sue', 'data'),
#     [Input('date_user', 'start_date'),
#      Input('date_user', 'end_date'),
#      ])
# def update_table_top_etsp(start_date_user, end_date_user):
#     sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]
#     top_user_sue_filtered_df = pd.DataFrame(sue_filtered_df.groupby('user')['count_task'].sum()
#                                             .sort_values(ascending=False).head()
#                                             .reset_index()).rename(columns={'user': 'Пользователь',
#                                                                             'count_task': 'Обращения'})
#     return top_user_sue_filtered_df.to_dict('records')


@app.callback(
    Output('date_user', 'disabled'),
    Output('month_choice', 'disabled'),
    Output('users_figure', 'figure'),
    Output('tasks', 'children'),
    Output('tasks', 'style'),
    Output('users', 'children'),
    Output('users', 'style'),
    Output('etsp-time', 'children'),
    Output('sue-time', 'children'),
    Output('osp-time', 'children'),
    Output('support_figure', 'figure'),
    Output('sue_avaria', 'data'),
    Output('sue_avaria', 'style_data'),
    Output('table_top_etsp', 'data'),
    Output('table_top_sue', 'data'),
    Output('sue_avaria', 'tooltip_data'),
    [Input('my-toggle-switch', 'value'),
     Input('date_user', 'start_date'),
     Input('date_user', 'end_date'),
     Input('month_choice', 'value'),
     ])
def update_figure_user(value, start_date_user, end_date_user, choosen_month):
    if not value:
        etsp_filtered_df = etsp_df[
            (etsp_df['start_date'] >= start_date_user) & (etsp_df['start_date'] <= end_date_user)]
        sue_filtered_df = sue_df[(sue_df['start_date'] >= start_date_user) & (sue_df['start_date'] <= end_date_user)]
        osp_filtered_df = osp_df[(osp_df['start_date'] >= start_date_user) & (osp_df['start_date'] <= end_date_user)]
        sue_avaria_filtered_df = sue_avaria_df[(sue_avaria_df['Дата обращения'] >= start_date_user) &
                                               (sue_avaria_df['Дата обращения'] <= end_date_user)]
        if int(start_date_user[5:7]) > 1:
            etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == (int(start_date_user[5:7]) - 1)]
            sue_prev_filt_df = sue_df[sue_df['month_open'] == (int(start_date_user[5:7]) - 1)]
            osp_prev_filt_df = osp_df[osp_df['month_open'] == (int(start_date_user[5:7]) - 1)]
        else:
            etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == 12]
            sue_prev_filt_df = sue_df[sue_df['month_open'] == 12]
            osp_prev_filt_df = osp_df[osp_df['month_open'] == 12]
    else:
        if int(choosen_month) > 1:
            etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == (int(choosen_month) - 1)]
            sue_prev_filt_df = sue_df[sue_df['month_open'] == (int(choosen_month) - 1)]
            osp_prev_filt_df = osp_df[osp_df['month_open'] == (int(choosen_month) - 1)]
        else:
            etsp_prev_filt_df = etsp_df[etsp_df['month_open'] == 12]
            sue_prev_filt_df = sue_df[sue_df['month_open'] == 12]
            osp_prev_filt_df = osp_df[osp_df['month_open'] == 12]
        etsp_filtered_df = etsp_df[etsp_df['month_open'] == int(choosen_month)]
        sue_filtered_df = sue_df[sue_df['month_open'] == int(choosen_month)]
        osp_filtered_df = osp_df[osp_df['month_open'] == int(choosen_month)]
        sue_avaria_filtered_df = sue_avaria_df[sue_avaria_df['month_open'] == int(choosen_month)]

    etsp_count_tasks = etsp_filtered_df['count_task'].sum()
    sue_count_tasks = sue_filtered_df['count_task'].sum()
    osp_count_tasks = osp_filtered_df['count_task'].sum()

    etsp_prev_count_tasks = etsp_prev_filt_df['count_task'].sum()
    sue_prev_count_tasks = sue_prev_filt_df['count_task'].sum()
    osp_prev_count_tasks = osp_prev_filt_df['count_task'].sum()

    etsp_avg_time = CountMeanTime(etsp_filtered_df)
    sue_avg_time = CountMeanTime(sue_filtered_df)
    osp_avg_time = CountMeanTime(osp_filtered_df)

    fig_support = go.Figure(go.Bar(y=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
                                   x=['ЕЦП', 'СУЭ', 'ОСП'],
                                   base=0,
                                   marker=dict(color=['#a92b2b', '#37a17c', '#a2d5f2']),
                                   text=[etsp_count_tasks, sue_count_tasks, osp_count_tasks],
                                   textposition='auto'))
    fig_support.update_layout(autosize=True,
                              # height=700,
                              legend=dict(
                                  orientation="h",
                                  yanchor="bottom",
                                  y=0.2,
                                  xanchor="right",
                                  x=0.5),
                              paper_bgcolor='#ebecf1',
                              plot_bgcolor='#ebecf1'
                              )
    fig_support.update_xaxes(ticks="inside",
                             tickson="boundaries")

    total_curr_tasks = etsp_count_tasks + sue_count_tasks + osp_count_tasks
    total_prev_tasks = etsp_prev_count_tasks + sue_prev_count_tasks + osp_prev_count_tasks
    diff_tasks = total_curr_tasks - total_prev_tasks

    if diff_tasks > 0:
        style_tasks = {'font-size': '2em', 'color': 'green'}
        diff_tasks = '+' + str(diff_tasks)
    elif diff_tasks == 0:
        style_tasks = {'font-size': '2em'}
        diff_tasks = str(diff_tasks)
    else:
        style_tasks = {'font-size': '2em', 'color': 'red'}
        diff_tasks = str(diff_tasks)

    total_tasks = ''.join([str(total_curr_tasks), ' (', diff_tasks, ')'])

    total_curr_users = len(etsp_filtered_df['Имя затронутого пользователя'].unique()) + len(
        sue_filtered_df['user'].unique()) + len(osp_filtered_df['Пользователь'].unique())
    total_prev_users = len(etsp_prev_filt_df['Имя затронутого пользователя'].unique()) + len(
        sue_prev_filt_df['user'].unique()) + len(osp_prev_filt_df['Пользователь'].unique())
    diff_users = total_curr_users - total_prev_users

    if diff_users > 0:
        style_users = {'font-size': '2em', 'color': 'green'}
        diff_users = '+' + str(diff_users)
    elif diff_users == 0:
        style_users = {'font-size': '2em'}
        diff_users = str(diff_users)
    else:
        style_users = {'font-size': '2em', 'color': 'red'}
        diff_users = str(diff_users)

    total_users = ''.join([str(total_curr_users), ' (', diff_users, ')'])

    labels_figure_support = ["ЕЦП", "СУЭ", "ОСП"]
    values_figure_support = [etsp_filtered_df['count_task'].sum(), sue_filtered_df['count_task'].sum(),
                             osp_filtered_df['count_task'].sum()]
    colors = ['#a92b2b', '#37a17c', '#a2d5f2']

    fig = go.Figure(go.Pie(labels=labels_figure_support, values=values_figure_support, marker_colors=colors))
    fig.update_traces(hoverinfo="label+percent+name")

    fig.update_layout(paper_bgcolor='#ebecf1', showlegend=True)

    top_user_etsp_filtered_df = pd.DataFrame(etsp_filtered_df.groupby('Имя затронутого пользователя')['count_task']
                                             .sum().sort_values(ascending=False).head().reset_index()).rename(
        columns={'Имя затронутого пользователя': 'Пользователь', 'count_task': 'Обращения'})

    top_user_sue_filtered_df = pd.DataFrame(sue_filtered_df.groupby('user')['count_task'].sum().sort_values(
        ascending=False).head().reset_index()).rename(columns={'user': 'Пользователь', 'count_task': 'Обращения'})

    if len(sue_avaria_filtered_df) > 0:
        style_data = dict(width='20%', backgroundColor='#ff847c')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in
                        sue_avaria_filtered_df.to_dict('records')]
        return (value, not value, fig_support, total_tasks, style_tasks, total_users, style_users, etsp_avg_time,
                sue_avg_time, osp_avg_time, fig, sue_avaria_filtered_df.to_dict('records'), style_data,
                top_user_etsp_filtered_df.to_dict('records'), top_user_sue_filtered_df.to_dict('records'), tooltip_data)
    else:
        style_data = dict(width='20%', backgroundColor='#c4fbdb')
        no_incident = [{'Дата': '-', 'Тип': 'Аварийных инциндентов нет', 'Номер': '-', 'Описание': '-',
                        'Плановое время': '-', 'Фактическое время': '-', 'Пользователь': '-', 'timedelta': '-',
                        'Отдел': '-', 'month_open': '-', 'month_solved': '-', 'count_task': '-', 'Дата обращения': '-',
                        'finish_date': '-'}]
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in
                        no_incident]
        return (value, not value, fig_support, total_tasks, style_tasks, total_users, style_users, etsp_avg_time,
                sue_avg_time, osp_avg_time, fig, no_incident, style_data, top_user_etsp_filtered_df.to_dict('records'),
                top_user_sue_filtered_df.to_dict('records'), tooltip_data)


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.1.4', port=8000)
