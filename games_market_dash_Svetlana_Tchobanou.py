import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
server = app.server

path_data = Path(Path(__file__).parent, 'games.csv')

df = pd.read_csv(path_data)
df.dropna(inplace=True)
df = df[df['Year_of_Release'] >= 2000]
df['Year_of_Release'] = df['Year_of_Release'].astype(int)

years_filter = dcc.RangeSlider(
                    id='crossfilter-year--slider',
                    min=df['Year_of_Release'].min(),
                    max=df['Year_of_Release'].max(),
                    step=1, 
                    pushable=False,
                    value=[df['Year_of_Release'].min(), df['Year_of_Release'].max()],
                    marks={str(year): str(year) for year in df['Year_of_Release'].unique()}
                    )

genres_filter = dcc.Dropdown(
                    id='crossfilter-genres',
                    options=dict(zip(df['Genre'].unique(), df['Genre'].unique())),
                    value=df['Genre'].unique(),
                    multi=True
                    )    
   
ratings_filter = dcc.Dropdown(
                    id='crossfilter-ratings',
                    options=dict(zip(df['Rating'].unique(), df['Rating'].unique())),
                    value=df['Rating'].unique(),
                    multi=True
                     )    
    
graf1 = dcc.Graph(id='stacked-area1')
graf2 = dcc.Graph(id='scatter-plot2')

app.layout = html.Div([
    html.H2(children="Интерактивный дашборд. Статистика по играм.",
            style={'padding': '10px 5px 5px 5px', "fontSize": "32px"}),
    
    html.Div("Предназначен для обзора статистики по играм, выпущенным с 2000 по 2016 год. "
            "Фильтры по жанрам и рейтингам поддерживают множественный выбор, "
            "фильтр по годам выпуска (внизу страницы) интервальный.",
             style={'padding': '10px 5px 5px 5px',"fontSize": "24px" }), #инструкция
    
    html.Div([
        html.Div("Фильтр жанров",style={'width': '49%', 'display': 'inline-block',"fontSize": "20px"}),
        html.Div("Фильтр рейтингов", style={'width': '49%', 'float': 'right', 'display': 'inline-block',"fontSize": "20px"})

   ], style={'padding': '5px 5px 5px 5px'}),
    
    html.Div([

        html.Div(genres_filter, style={'width': '49%', 'display': 'inline-block'}),
        html.Div(ratings_filter, style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
        
    ], style={
        'padding': '10px 5px'
    }),
    
    html.H3(children=f'всего игр: {df["Name"].nunique()}', id='interactive-text1', style={'width': '49%', 'padding': '10px 10px 10px 10px'}),
    
    html.H2([

        html.Label("Stacked area plot, показывающий выпуск игр по годам и платформам",
                 style={'width': '49%', 'display': 'inline-block','padding': '0px 0px 5px 0px', "fontSize": "24px"}),

        html.Label(f"Scatter plot с разбивкой по жанрам (каждому жанру соответствует один цвет). По оси X - оценки игроков, по оси Y - оценки критиков", 
                 style={'width': '49%', 'float': 'right', 'display': 'inline-block', "fontSize": "24px"})
        
    ], style={'padding': '10px 0px'}),
    
    html.Div([
        html.Div(graf1, style={'width': '49%', 'display': 'inline-block', 'hight': '30%', 'padding': '0 20'}),
        html.Div(graf2, style={'display': 'inline-block', 'width': '49%', 'hight': '30%', 'padding': '0 20'}),
    ]),# style={'hight': '30%', 'padding': '0 20'}), 

    html.Div(years_filter, style={'width': '600px', 'padding': '0px 20px 20px 20px'})
])


@app.callback(
    [
        Output('stacked-area1', 'figure'),
        Output('scatter-plot2', 'figure'),
        Output('interactive-text1', 'children')
    ],
    [
        Input('crossfilter-genres', 'value'),
        Input('crossfilter-ratings', 'value'),
        Input('crossfilter-year--slider', 'value')
    ])
def update_data(genre_values,
                rating_values,
                year_values):
    list_years = [i for i in range(year_values[0], year_values[1] + 1)]
    dff = df.query('Year_of_Release in @list_years and Rating in @rating_values and Genre in @genre_values')

    fig2 = go.Figure(px.scatter(dff, x='User_Score', y='Critic_Score', color='Genre'))
    fig2['layout']['autosize'] = True
            
    data = dff.groupby(by=['Platform', 'Year_of_Release'],  as_index=False)\
              .agg({'Name': 'count'})\
              .rename(columns={'Name': 'num'})
    
    fig1 = go.Figure()

    for cur_plat in list(data.Platform.unique()):

        fig1.add_trace(go.Scatter(
            x=data.query('Platform == @cur_plat')['Year_of_Release'].values,
            y=data.query('Platform == @cur_plat')['num'].values,
            mode='lines',
            line=dict(width=0.5),
            name=cur_plat,
            text=data['Platform'],
            stackgroup='one' # define stack group
        ))
    fig1['layout']['autosize'] = True
    text = f'всего игр: {dff["Name"].nunique()}'
    
    return fig1, fig2, text

    
# if __name__ == '__main__':
#     app.run_server(debug=True)
    
    
    
    
    
    




















