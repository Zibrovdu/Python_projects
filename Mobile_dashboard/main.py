import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import date

current_month = date.today().month

df = pd.read_excel('data.xlsx', skiprows=7)
df = df.drop('Unnamed: 0', axis=1)
df.set_index(df.columns[0], inplace=True)
df = df.T
df['month'] = pd.to_datetime(df.index)
df['month'] = df['month'].dt.month

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
            dcc.Slider(id='month-slider_1',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=current_month,
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ], className='six columns'),
        html.Div([
            html.H3('Сопроводение пользователей'),
            dcc.Graph(id='tech'),
            dcc.Slider(id='month-slider_2',
                       min=df['month'].min(),
                       max=df['month'].max(),
                       value=df['month'].min(),
                       marks={str(month): str(month) for month in df['month'].unique()},
                       step=None)
        ], className='six columns'),
    ], className='row')
])


@app.callback(
    Output('users', 'figure'),
    [Input('month-slider_1', 'value')])
def update_figure_user(selected_month_1):
    df1 = pd.read_excel('data.xlsx', skiprows=7)
    df1 = df1.drop('Unnamed: 0', axis=1)
    df1.set_index(df1.columns[0], inplace=True)
    df1 = df1.T
    df1['month'] = pd.to_datetime(df1.index)
    df1['month'] = df1['month'].dt.month

    filtered_df_1 = df1[df1['month'] == selected_month_1]

    trace_office = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя в офисе']),
                              name='работа в офисе',
                              line=dict(color='orange', width=3))
    trace_online = go.Scatter(x=list(filtered_df_1.index),
                              y=list(filtered_df_1['Сопровождение пользователя на удаленной работе']),
                              name='удаленная работа',
                              line=dict(color='blue', width=3))

    data_1 = [trace_office, trace_online]

    layout_1 = dict(
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
                    # dict(count=1,
                    #      label='1y',
                    #      step='year',
                    #      stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date_1'
        )
    )

    return {
        "data": data_1,
        "layout": layout_1}


@app.callback(
    Output('tech', 'figure'),
    [Input('month-slider_2', 'value')])
def update_figure_tech(selected_month_2):
    df2 = pd.read_excel('data.xlsx', skiprows=7)
    df2 = df2.drop('Unnamed: 0', axis=1)
    df2.set_index(df2.columns[0], inplace=True)
    df2 = df2.T
    df2['month'] = pd.to_datetime(df2.index)
    df2['month'] = df2['month'].dt.month

    filtered_df_2 = df2[df2['month'] == selected_month_2]

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

    data_2 = [trace_rtk, trace_sue, trace_sue_osp]

    layout_2 = dict(
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
            type='date_2'
        )
    )

    return {
        "data": data_2,
        "layout": layout_2
    }


if __name__ == "__main__":
    app.run_server(debug=True, host='192.168.2.10', port=8050)