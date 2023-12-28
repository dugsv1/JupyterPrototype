# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 15:48:00 2023

@author: Sven
"""
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import json
from pandas import json_normalize
import folium
from dash.dependencies import Input, Output

json_file_path = '../data/sample.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

df = json_normalize(data['returnValue'])
avg_response_times = df.groupby(
    'natureCode')['initialResponseMinutes'].mean().reset_index()
df['initialDispatch'] = pd.to_datetime(
    df['initialDispatch'])  # Convert to datetime
df['month'] = df['initialDispatch'].dt.month

# Get a list of unique months for the dropdown
month_names = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Create a new column with month names
df['month_name'] = df['month'].map(lambda x: month_names[x-1])
months = df['month_name'].unique()


def create_modified_map(map_name, data, center=[45.5236, -122.6750], zoom_start=12):
    # Create a Folium map
    m = folium.Map(location=center, zoom_start=zoom_start)

    # Loop through the data and add a marker for each call
    for index, row in data.iterrows():
        # Extract information for the marker
        latitude = row['latitude']
        longitude = row['longitude']
        popup_text = f"Call ID: {row['callId']}<br>Nature Code: {row['natureCode']}<br>Initial Response: {row['initialResponseMinutes']} mins"

        # Create and add the marker to the map
        folium.CircleMarker(
            location=[latitude, longitude],
            radius=2,
            popup=popup_text,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    # Save the map to an HTML file
    m.save(f'../temp/{map_name}.html')
    return f'../temp/{map_name}.html'


map_name = "basic_map"
map_file = create_modified_map(
    map_name, df, center=[44.5646, -123.2620])

fig = px.bar(avg_response_times, x='natureCode', y='initialResponseMinutes',
             title='Average Initial Response Time by Nature Code')
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Interactive Dash App'),
    html.Div('Explore initial response times and locations.'),
    html.Label('Select Month'),
    dcc.Dropdown(
        id='month-dropdown',
        options=[{'label': month, 'value': month} for month in months],
        value=months[0] if len(months) > 0 else None,
        style={'width': '200px'}
    ),
    dcc.Graph(id='avg-response-time-graph'),
    dcc.Graph(id='locations-map'),  # Map for locations
    html.Div(id='space', style={'height': '20px'}),
    html.Iframe(id='map', srcDoc=open(map_file, 'r').read(),
                style={'width': '100%', 'height': '600px'})

], style={'margin-left': '40px', 'margin-right': '40px'})  # Apply margin to the entire page


# Callback to update the bar chart


@app.callback(
    Output('avg-response-time-graph', 'figure'),
    [Input('month-dropdown', 'value')]
)
def update_avg_response_times(selected_month):
    if not selected_month:  # Check if selected_month is None or empty
        return px.bar(avg_response_times, x='natureCode', y='initialResponseMinutes',
                      title='Average Initial Response Time by Nature Code')
    # Filter the data for the selected month
    filtered_df = df[df['month_name'] == selected_month]
    # Calculate average response times by nature code
    avg_response = filtered_df.groupby(
        'natureCode')['initialResponseMinutes'].mean().reset_index()

    fig = px.bar(avg_response, x='natureCode', y='initialResponseMinutes',
                 title=f'Average Initial Response Time by Nature Code for Month {selected_month}')
    return fig


# Callback for the locations map
@app.callback(
    Output('locations-map', 'figure'),
    [Input('month-dropdown', 'value')]
)
def update_locations_map(selected_month):
    if not selected_month:
        # Show all data if no month is selected
        fig = px.scatter_mapbox(df, lat='latitude', lon='longitude',
                                color='natureCode', size='initialResponseMinutes',
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                title='Locations and Initial Response Times',
                                zoom=10)
        fig.update_layout(mapbox_style='open-street-map')
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600)
        return fig

    # Filter the data for the selected month
    filtered_df = df[df['month_name'] == selected_month]
    fig = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude',
                            color='natureCode', size='initialResponseMinutes',
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            title=f'Locations and Initial Response Times for Month {selected_month}',
                            zoom=10)
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600)
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
