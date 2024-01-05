# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 14:52:32 2024

@author: Sven
"""

import json
import random
from datetime import date, datetime

import numpy as np
import pandas as pd
from pandas import json_normalize
from pandas.api.types import CategoricalDtype

import holoviews as hv
import geoviews as gv
import hvplot.pandas
import panel as pn
import panel.widgets as pnw

from bokeh.layouts import row, column, gridplot
from bokeh.models import (ColumnDataSource, DataTable, HoverTool, IntEditor,
                          NumberEditor, NumberFormatter, SelectEditor,
                          StringEditor, StringFormatter, TableColumn, DatetimeRangeSlider,
                          CustomJS, MultiChoice)
from bokeh.plotting import figure, show
from bokeh.transform import factor_cmap
from bokeh.transform import factor_cmap, factor_mark
from bokeh.palettes import RdBu
from bokeh.io import curdoc
import xyzservices.providers as xyz

from holoviews import opts


#### PROCESS DATA ######
json_file_path = '../data/sample.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)
df = json_normalize(data['returnValue'])
df['initialDispatch'] = pd.to_datetime(df['initialDispatch'])
df['date'] = df['initialDispatch'].dt.date
month_names = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
month_cat_type = CategoricalDtype(
    categories=month_names,
    ordered=True
)
df['month_name'] = df['initialDispatch'].dt.month_name()
df['month_name'] = df['month_name'].astype(month_cat_type)

units = ['E131', 'M122', 'E132', 'M133']
df['unit'] = [random.choice(units) for _ in range(len(df))]
df['unit'] = df['unit'].astype(str)
avg_response_times = df.groupby(
    'unit')['initialResponseMinutes'].mean().reset_index()
print(df.head(1))

#### DEFINE FUNCTIONS ######


def create_bar_chart(dataframe):
    bar_chart = figure(title='Average Initial Response Time by Unit', x_axis_label='Unit',
                       y_axis_label='Avg Initial Response Time (minutes)', x_range=dataframe['unit'])
    bar_chart.vbar(x='unit', top='initialResponseMinutes',
                   source=dataframe, width=0.7, color="navy")
    return bar_chart


def create_hvplot_bar_chart(dataframe):
    # Use hvPlot to create a bar chart
    bar_chart = dataframe.hvplot.bar(
        x='unit',
        y='initialResponseMinutes',
        title='Average Initial Response Time by Unit',
        xlabel='Unit',
        ylabel='Avg Initial Response Time (minutes)',
        height=400,
        width=600,
        color="navy"
    )
    return bar_chart


# Function to create a histogram using Bokeh
def create_histogram(dataframe):
    # Calculate histogram data
    hist, edges = np.histogram(dataframe['initialResponseMinutes'], bins=20)
    hist_df = pd.DataFrame(
        {'hist': hist, 'left': edges[:-1], 'right': edges[1:]})
    source = ColumnDataSource(hist_df)

    # Create the histogram figure
    hist_fig = figure(
        title='Histogram', x_axis_label='Initial Response Minutes', y_axis_label='Count')
    hist_fig.quad(bottom=0, top='hist', left='left', right='right',
                  source=source, fill_color="navy", line_color="white", alpha=0.5)

    return hist_fig

# Callback function for the range slider


def update_plot(attr, old, new):
    start, end = new  # Unpack the tuple to get start and end
    # Convert from Unix time in milliseconds
    start = pd.to_datetime(start, unit='ms')
    # Convert from Unix time in milliseconds
    end = pd.to_datetime(end, unit='ms')

    # Filter the data based on the selected date range
    filtered = df[(df['initialDispatch'] >= start)
                  & (df['initialDispatch'] <= end)]

    # Update the data in the plot (You'll need to define create_bar_chart function)
    new_avg_response_times = filtered.groupby(
        'unit')['initialResponseMinutes'].mean().reset_index()
    source.data = new_avg_response_times


def wgs84_to_web_mercator(df, lon="longitude", lat="latitude"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df


#### BAR CHART AND HISTOGRAM ######
min_date_timestamp = df['initialDispatch'].min(
).timestamp() * 1000  # Convert to milliseconds
max_date_timestamp = df['initialDispatch'].max(
).timestamp() * 1000  # Convert to milliseconds

# Create the range slider with timestamps
date_range_slider = DatetimeRangeSlider(start=min_date_timestamp, end=max_date_timestamp,
                                        value=(min_date_timestamp,
                                               max_date_timestamp),
                                        step=1, title="Date Range")

date_range_slider.on_change('value', update_plot)

# Create the plots
bar_chart = create_bar_chart(avg_response_times)
histogram = create_histogram(df)

#### MAP AND TABLE ######

df = wgs84_to_web_mercator(df)
expected_factors = ['E132', 'M122']
color_mapper = factor_cmap(field_name='unit', palette=[
                           RdBu[3][1], RdBu[3][0]], factors=expected_factors)
df['color'] = [RdBu[3][1] if 'E' in unit else RdBu[3][0]
               for unit in df['unit']]
bar_source = ColumnDataSource(df)

columns = [
    TableColumn(field="callId", title="Call ID", formatter=StringFormatter()),
    TableColumn(field="initialDispatch", title="Initial Dispatch",
                formatter=StringFormatter()),
    TableColumn(field="natureCode", title="Nature Code",
                formatter=StringFormatter()),
    TableColumn(field="streetAddress", title="Street Address",
                formatter=StringFormatter()),
    TableColumn(field="longitude", title="Longitude (Web Mercator)",
                formatter=StringFormatter()),
    TableColumn(field="latitude", title="Latitude (Web Mercator)",
                formatter=StringFormatter()),
    TableColumn(field="initialResponseMinutes",
                title="Initial Response Minutes", formatter=StringFormatter()),
    TableColumn(field="fullComplementMinutes",
                title="Full Complement Minutes", formatter=StringFormatter()),
    TableColumn(field="notes", title="Notes", formatter=StringFormatter()),
    TableColumn(field="date", title="Date", formatter=StringFormatter()),
    TableColumn(field="month_name", title="Month Name",
                formatter=StringFormatter()),
    TableColumn(field="unit", title="Unit", formatter=StringFormatter()),
    TableColumn(field="x", title="X (Web Mercator)",
                formatter=StringFormatter()),
    TableColumn(field="y", title="Y (Web Mercator)",
                formatter=StringFormatter()),
]

data_table = DataTable(source=bar_source, columns=columns, editable=True,
                       width=1200, index_position=-1, index_header="row index", index_width=60)

# Coordinate conversion to Mercator, required for Bokeh
x_min, x_max = df['x'].min() - 1000, df['x'].max() + 1000
y_min, y_max = df['y'].min() - 1000, df['y'].max() + 1000
p = figure(x_range=(x_min, x_max), y_range=(y_min, y_max),
           x_axis_type="mercator", y_axis_type="mercator",
           width=1200, height=600, tools="pan,wheel_zoom,lasso_select,reset", active_drag="pan",
           active_scroll="wheel_zoom")

p.xaxis.major_label_text_font_size = '0pt'
p.yaxis.major_label_text_font_size = '0pt'
p.add_tile(xyz.OpenStreetMap.Mapnik)
p.circle(x='x', y='y', size=10, fill_color='color',
         fill_alpha=0.8, source=bar_source, legend_field='unit')


#### BUILDING SIDEBAR ######
unique_units = sorted(df['unit'].unique().tolist())
unit_selector = MultiChoice(
    value=[""], options=unique_units, title="Select Units")

#### CONVERTING PLOTS TO PANEL PANES ######
map_pane = pn.pane.Bokeh(p)
table_pane = pn.pane.Bokeh(data_table)
bar_chart_pane = pn.pane.Bokeh(bar_chart)
histogram_pane = pn.pane.Bokeh(histogram)


#### FILTER SUMMARY ######
filter_summary = pn.pane.Markdown("""
### Filter Summary
- Filter 1: Active
- Filter 2: Inactive
""")

# Simulate a small map for geofencing overview
geofence_map = pn.pane.Markdown("### Geofence Map Here")
geofence_map_card = pn.Card(geofence_map, title="Geofence Map")
filter_summary_card = pn.Card(filter_summary, title="Filter Summary")
spacer = pn.Spacer(height=20)
right_panel = pn.Column(filter_summary_card, spacer,
                        geofence_map_card, width=300)

main_content = pn.Column(
    date_range_slider,
    pn.Row(bar_chart_pane, histogram_pane),
    pn.Column(map_pane, table_pane)
)

template = pn.template.FastListTemplate(
    title="Levrum Dashboard",
    # Add any additional widgets you want in the sidebar
    sidebar=unit_selector,
)
template.main.append(
    pn.Row(main_content, right_panel)
)

template.servable()
