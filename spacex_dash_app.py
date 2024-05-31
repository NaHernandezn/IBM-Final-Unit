# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site_dropdown',
        options=[
            {'label': 'All sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload_slider',
        min=min_payload,
        max=max_payload+1000,
        step=1000,
        marks={i: str(i) for i in range(int(min_payload), int(max_payload) + 1000, 2500)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site_dropdown', component_property='value')
)
def get_pie_chart(site_dropdown):
    if site_dropdown == 'ALL':
        # Calculate the total successful and failed launches for all sites
        fig = px.pie(
            spacex_df, 
            names='LaunchSite', 
            values='class', 
            title='Total Successful Launches by Site'
        )
    else:
        # Filter the dataframe for the selected site
        filtered_df = spacex_df[spacex_df['LaunchSite'] == site_dropdown]
        # Calculate the total successful and failed launches for the selected site
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(
            success_counts, 
            names='class', 
            values='count', 
            title=f'Total Successful Launches for site {site_dropdown}'
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value'),
     Input(component_id='payload_slider', component_property='value')]
)
def get_scatter_plot(site_dropdown, payload_slider):
    low, high = payload_slider
    if site_dropdown == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
        plot = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        filtered_df = spacex_df[(spacex_df['LaunchSite'] == site_dropdown) & 
                                (spacex_df['Payload Mass (kg)'] >= low) & 
                                (spacex_df['Payload Mass (kg)'] <= high)]
        plot = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title=f'Payload vs. Outcome for Site {site_dropdown}'
        )
    return plot

# Run the app
if __name__ == '__main__':
    app.run_server()