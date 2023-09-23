# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go  # Add this import

# Read the airline data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(id='site-dropdown', options=[
        {'label': 'All Sites', 'value': 'ALL'},
        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
    ], value='ALL', placeholder="Select a Launch Site here", searchable=True),
    
    html.Br(),

    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={0: '0', 100: '100'}, value=[min_payload, max_payload]),

    html.Div([
        dcc.Graph(
            id='success-payload-scatter-chart',
            figure={
                'data': [
                    go.Scatter(
                        x=spacex_df[spacex_df['class'] == 1]['Payload Mass (kg)'],
                        y=spacex_df[spacex_df['class'] == 1]['class'],
                        mode='markers',
                        marker=dict(color='green'),
                        name='Successful Launch'
                    ),
                    go.Scatter(
                        x=spacex_df[spacex_df['class'] == 0]['Payload Mass (kg)'],
                        y=spacex_df[spacex_df['class'] == 0]['class'],
                        mode='markers',
                        marker=dict(color='red'),
                        name='Failed Launch'
                    ),
                ],
                'layout': go.Layout(
                    xaxis={'title': 'Payload Mass (kg)'},
                    yaxis={'title': 'Launch Success (1=Success, 0=Failure)'},
                    title='Payload vs. Launch Success Scatter Plot',
                ),
            }
        ),
    ]),
])

# Callback for success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site == 'ALL':
        fig = px.pie(
            filtered_df,
            values='class',
            names='Launch Site',
            title='Success Count by Launch Site'
        )
        return fig
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.pie(
            site_filtered_df,
            names='class',
            title=f'Success Count for {entered_site}'
        )
        return fig

# Callback for success-payload-scatter-chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id="payload-slider", component_property="value")
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    scatter_chart = go.Figure()

    for booster_version in filtered_df['Booster Version']:
        data = filtered_df[filtered_df['Booster Version'] == booster_version]
        scatter_chart.add_trace(
            go.Scatter(
                x=data['Payload Mass (kg)'],
                y=data['class'],
                mode='markers',
                name=booster_version,
                text=data['Booster Version'],
                marker=dict(size=10),
            )
        )

    scatter_chart.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Launch Outcome (1=Success, 0=Failure)",
        title="Payload vs. Launch Outcome Scatter Plot",
        showlegend=True,
    )

    return scatter_chart

# Run the app
if __name__ == '__main__':
    app.run_server()
