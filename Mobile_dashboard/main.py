import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd

data_df = pd.read_excel('data.xlsx', skiprows=7)
data_df = data_df.drop('Unnamed: 0', axis=1)
data_df.set_index(data_df.columns[0], inplace=True)
df = data_df.T
df['month'] = pd.to_datetime(df.index)
df['month'] = df['month'].dt.month
print(df.head())

trace_rtk = go.Scatter(x=list(df.index),
                       y=list(df['РТК']),
                       name='РТК',
                       line=dict(color='#F44242', width=3))

trace_sue = go.Scatter(x=list(df.index),
                       y=list(df['СУЭ']),
                       name='СУЭ',
                       line=dict(color='green', width=3))

trace_sue_osp = go.Scatter(x=list(df.index),
                           y=list(df['СУЭ ОСП']),
                           name='СУЭ ОСП',
                           line=dict(color='blue', width=3))
# trace_office = go.Scatter(x=list(df.index),
#                           y=list(df['Сопровождение пользователя в офисе']),
#                           name='работа в офисе',
#                           line=dict(color='orange', width=3))
# trace_online = go.Scatter(x=list(df.index),
#                           y=list(df['Сопровождение пользователя на удаленной работе']),
#                           name='удаленная работа',
#                           line=dict(color='blue', width=3))

external_stylesheets = ['assets/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H2("Межрегиональное бухгалтерское УФК"),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    html.Div([
        html.Div([
            html.H3('Обращения в техническую поддержку'),
            dcc.Graph(id='users'),

            dcc.Slider(id='month-slider',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=df['month'].min(),
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ], className='six columns'),
        html.Div([
            html.H3('Сопроводение пользователей'),
            dcc.Graph(
                id='tech',
                figure={
                    'data': [trace_rtk, trace_sue, trace_sue_osp],
                    'layout': dict(
                        title='Сопроводение пользователей',
                        xaxis=dict(
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1,
                                         label='1w',
                                         step='week',
                                         stepmode='backward'),
                                    dict(count=1,
                                         label='1m',
                                         step='month',
                                         stepmode='backward'),
                                    dict(count=6,
                                         label='6m',
                                         step='month',
                                         stepmode='backward'),
                                    dict(count=1,
                                         label='1y',
                                         step='year',
                                         stepmode='backward'),
                                    dict(step='all')
                                ])
                            ),
                            rangeslider=dict(
                                visible=True
                            ),
                            type='date'
                        )
                    )
                }
            )

        ], className='six columns'),
    ], className='row')
])


@app.callback(
    Output('users', 'figure'),
    [Input('month-slider', 'value')])
def update_figure(selected_month):
    filtered_df = df[df.month == selected_month]

    trace_office = go.Scatter(x=list(filtered_df.index),
                              y=list(filtered_df['Сопровождение пользователя в офисе']),
                              name='работа в офисе',
                              line=dict(color='orange', width=3))
    trace_online = go.Scatter(x=list(filtered_df.index),
                              y=list(filtered_df['Сопровождение пользователя на удаленной работе']),
                              name='удаленная работа',
                              line=dict(color='blue', width=3))

    data = [trace_office, trace_online]

    layout = dict(
        title='Обращения в техническую поддержку',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1w',
                         step='week',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    # data.update_layout(transition_duration=500)

    return {
        "data": data,
        "layout": layout
    }


# @app.callback(Output('users', 'figure'),
#               [Input('submit-button', 'n_clicks')],
#               [State('input', 'value')]
#               )
# def update_fig(n_clicks, input_value)

# data = [trace_rtk, trace_sue, trace_sue_osp]

# updatemenus = list([
#     dict(
#         buttons=list([
#             dict(
#                 args=[{'visible': [True, False, False]}],
#                 label='Line',
#                 method='update'
#             ),
#             dict(
#                 args=[{'visible': [False, True, False]}],
#                 label='Candle',
#                 method='update'
#             ),
#             dict(
#                 args=[{'visible': [False, False, True]}],
#                 label='Bar',
#                 method='update'
#             ),
#         ]),
#         direction='down',
#         pad={'r': 10, 't': 10},
#         showactive=True,
#         x=0,
#         xanchor='left',
#         y=1.05,
#         yanchor='top'
#     ),
# ])
#
# layout = dict(
#     # title=input_value,
#     # updatemenus=updatemenus,
#     autosize=False,
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                      label='1w',
#                      step='week',
#                      stepmode='backward'),
#                 dict(count=1,
#                      label='1m',
#                      step='month',
#                      stepmode='backward'),
#                 dict(count=6,
#                      label='6m',
#                      step='month',
#                      stepmode='backward'),
#                 dict(count=1,
#                      label='1y',
#                      step='year',
#                      stepmode='backward'),
#                 dict(step='all')
#             ])
#         ),
#         rangeslider=dict(
#             visible=True
#         ),
#         type='date'
#     )
#
# )
#
# return {'data': data,
#         'layout': layout
#         }


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.10', port=8050)
