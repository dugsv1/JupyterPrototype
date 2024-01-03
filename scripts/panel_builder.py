import numpy as np
import panel as pn
import pandas as pd

from bokeh.layouts import row,column
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

# Create a sample DataFrame
df = pd.DataFrame({
    'x': range(1, 101),
    'y': np.random.randn(100).cumsum()
})

# Function to create a scatter plot using Bokeh
def create_scatter_plot(dataframe):
    source = ColumnDataSource(dataframe)
    scatter_fig = figure(title='Scatter Plot', x_axis_label='x', y_axis_label='y', sizing_mode="scale_width")
    scatter_fig.scatter('x', 'y', source=source, size=8, color="navy", alpha=0.5)
    return scatter_fig

# Function to create a histogram using Bokeh
def create_histogram(dataframe):
    hist, edges = np.histogram(dataframe['y'], bins=20)
    hist_df = pd.DataFrame({'hist': hist, 'left': edges[:-1], 'right': edges[1:]})
    source = ColumnDataSource(hist_df)
    
    hist_fig = figure(title='Histogram', x_axis_label='y', y_axis_label='Count', sizing_mode="scale_width")
    hist_fig.quad(bottom=0, top='hist', left='left', right='right', source=source, fill_color="navy", line_color="white", alpha=0.5)
    return hist_fig

# Create plots
scatter_plot = create_scatter_plot(df)
histogram = create_histogram(df)
