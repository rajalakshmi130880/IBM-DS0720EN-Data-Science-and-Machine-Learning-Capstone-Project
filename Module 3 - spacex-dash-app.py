# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Create app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='All Sites',
        placeholder='Select a Launch Site Here',
        searchable=True
    ),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(launch_site):
    if launch_site == 'All Sites':
        df = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(df, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == launch_site]
        fig = px.pie(site_df, names='class',color='class',
                    color_discrete_map={1: 'green', 0: 'red'},
                    title=f'Success vs Failure for Site {launch_site}')
    return fig

# Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_payload_chart(launch_site, payload_range):
    low, high = payload_range
    df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]

    if launch_site != 'All Sites':
        df = df[df['Launch Site'] == launch_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=f'Correlation Between Payload and Success for {launch_site}'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)