# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Br(),
    dcc.Dropdown(id='site-dropdown',
                options=[
                    {'label': 'All Sites', 'value': 'ALL'},
                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}               
                ],
                value='ALL',
                placeholder="Select Launch Site",
                searchable=True
                ),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={
            0: '0 kg',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        ),
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, use the entire dataset
        success_per_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            success_per_site,
            values='class',         # Now this represents sum of successes per site
            names='Launch Site',    # Sites as labels
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # For specific site, filter the dataframe
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count the class values (usually 0 for failure, 1 for success)
        class_counts = filtered_df['class'].value_counts().reset_index()
        # Rename columns for clarity
        class_counts.columns = ['class', 'count']
        fig = px.pie(
            class_counts,
            names='class',  # Labels (class values)
            values='count',   # the class labels (0 or 1)
            title=f'Success vs Failure for site {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
               Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])

def get_scatter(entered_site,range):
    if entered_site == 'ALL':
        filtered_range_df = spacex_df[(spacex_df['Payload Mass (kg)']>=range[0])&(spacex_df['Payload Mass (kg)']<range[1])]
        fig = px.scatter(filtered_range_df, x="Payload Mass (kg)", y="class",color="Booster Version Category",title='Payload vs Success for All Sites')
        return fig
    else:
        filtered_range_df = spacex_df[(spacex_df['Payload Mass (kg)']>=range[0])&(spacex_df['Payload Mass (kg)']<range[1])]
        filtered_df = filtered_range_df[filtered_range_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",color="Booster Version Category",title='Payload vs Success for Site '+entered_site)
        return fig
        
# Run the app
if __name__ == '__main__':
    app.run_server()
