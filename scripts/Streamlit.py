import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import os
import warnings
import json
from pandas import json_normalize
import folium
from folium.plugins import HeatMap
from pandas.api.types import CategoricalDtype
from branca.colormap import linear
# Use session state to track if data is loaded
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False
if 'run_on_save' not in st.session_state:
    st.session_state.run_on_save = True  # Set default value
warnings.filterwarnings('ignore')
        
# Function to load data
def load_data(uploaded_file):
    data = json.load(uploaded_file)
    return json_normalize(data['returnValue'])

# Functions to create visualizations
def create_chart(dataframe, visual='bar'):
    if visual == 'bar':
        return px.bar(dataframe, x='natureCode', y='initialResponseMinutes',
                      title='Average Initial Response Times by NatureCode')
    elif visual =='hist' or visual == 'histogram':
        return px.histogram(dataframe, x='natureCode', title='Frequency of NatureCode Types')

def create_folium_map(dataframe, map_type='marker'):
    center = [dataframe['latitude'].mean(), dataframe['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=13)
   
    min_response_time = dataframe['initialResponseMinutes'].min()
    max_response_time = dataframe['initialResponseMinutes'].max()
    colormap = linear.YlOrRd_09.scale(min_response_time, max_response_time)

    if map_type == 'marker':
        for _, row in dataframe.iterrows():            
            # Get the color from the color map
            marker_color = colormap(row['initialResponseMinutes'])
            
            # Create a popup text for each marker
            popup_text = f"Response Time: {row['initialResponseMinutes']} minutes"
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=2,
                popup=popup_text,
                color=marker_color,
                fill=True,
                fill_color=marker_color
            ).add_to(m)
            
        colormap.caption = 'Initial Response Time in Minutes'
        colormap.add_to(m)
    elif map_type == 'heatmap':
        HeatMap(dataframe[['latitude', 'longitude']], radius=15).add_to(m)
    return m



st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:",layout="wide")
st.title(" :bar_chart: Levrum Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader(":file_folder: Upload a json", type=['json'])


st.sidebar.header("Choose your filter: ")

# Load data and update session state
if uploaded_file is not None and not st.session_state['data_loaded']:
    df = load_data(uploaded_file)
    st.session_state['data_loaded'] = True
    avg_response_times = df.groupby(
        'natureCode')['initialResponseMinutes'].mean().reset_index()
    df['initialDispatch'] = pd.to_datetime(
        df['initialDispatch'])  # Convert to datetime
    #df['month'] = df['initialDispatch'].dt.month
    # Get a list of unique months for the dropdown
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    month_cat_type = CategoricalDtype(
        categories=month_names,
        ordered=True
    )
    df['month_name'] = df['initialDispatch'].dt.month_name()
    # Now convert to categorical with the defined type
    df['month_name'] = df['month_name'].astype(month_cat_type)
    st.session_state['df'] = df

col1, col2 = st.columns(2)

plot_height = 400
if st.session_state['data_loaded']:
    df = st.session_state['df']
    
    with col1:
        fig1 = create_chart(df)
        st.plotly_chart(fig1, use_container_width=True, height = plot_height)
        
    with col2:
        m = create_folium_map(df, map_type='marker')
        st_data = st_folium(m, use_container_width=True, height = plot_height)
        
    with col1:
        fig2 = create_chart(df, visual='hist')
        st.plotly_chart(fig2, use_container_width=True, height = plot_height)
        
    with col2:
        m = create_folium_map(df, map_type='heatmap')
        st_data = st_folium(m, use_container_width=True, height = plot_height)
else:
    st.write("Upload data to visualize it.")


# =============================================================================
# import subprocess
# command = "streamlit run streamlit.py"
# subprocess.run(command, shell=True)
# =============================================================================


