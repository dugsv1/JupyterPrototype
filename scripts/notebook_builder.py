import nbformat as nbf


def create_notebook(cell_structure):
    # Create a new notebook object
    nb = nbf.v4.new_notebook()

    # Initialize a list to hold all cells in order
    cells = [''] * (max(cell_structure.keys()) + 1)

    # Loop through the dictionary items
    for index, cell_info in cell_structure.items():
        title = cell_info.get('title', 'No Title')
        content = cell_info.get('content', '')
        purpose = cell_info.get('purpose', 'code')

        # Check the purpose and create the appropriate type of cell
        if purpose == "code":
            cell_text = f"# {title}\n{content}"
            cells[index] = nbf.v4.new_code_cell(cell_text)
        elif purpose == "narrative":
            cell_text = f"### {title}\n\n{content}"
            cells[index] = nbf.v4.new_markdown_cell(cell_text)

    # Filter out any empty placeholders and set the cells in the notebook
    nb.cells = [cell for cell in cells if cell]

    return nb


imports_Content = """
# Import necessary libraries
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px  # Plotly Express for easy plots
"""


executive_Content = """
## Automated Notebook for Code 3 Strategist Integration

### Automated Jupyter Notebook Creation
#### Integration with Code 3 Strategist

As part of our continuous effort to streamline data analysis and simulation modeling, we have developed an automated Jupyter Notebook that seamlessly integrates with **Code 3 Strategist**. This notebook is designed to enhance our modeling capabilities, enabling faster insights and more dynamic interaction with simulation data.

**Code 3 Strategist** is a sophisticated simulation modeling software used to analyze and predict complex systems. Our notebook acts as a complementary tool, allowing users to generate custom reports, visualize simulation results, and perform advanced data analysis through an intuitive, code-based interface.

### Features of the Automated Notebook:
- **Dynamic Content Generation:** Each notebook is automatically generated with predefined sections like 'Executive Summary', 'Chart Cell', and 'Map Cell', tailored to present the simulation results effectively.
- **Direct Integration:** Seamlessly pulls data from Code 3 Strategist simulations, ensuring that the most up-to-date and relevant information is always at hand.
- **Custom Visualizations:** Utilizes libraries like Matplotlib, Seaborn, and Plotly to create insightful charts and maps, enhancing the interpretability of complex data.
- **Editable and Interactive:** While the notebook is auto-generated, users have the full flexibility to add, remove, or modify content as needed to suit specific analysis requirements.

This automated solution represents a significant step forward in making simulation modeling more accessible and actionable. By bridging the gap between Code 3 Strategist and dynamic data analysis, we are empowering users to unlock deeper insights and drive strategic decision-making.

For more information on how to use the automated notebook or to get started with your own simulations, please contact our support team or visit our documentation portal.
"""

chart_cell_Content = """
# Code to display a bar chart using Seaborn
data = [4, 5, 6]
labels = ['Category 1', 'Category 2', 'Category 3']
sns.barplot(x=labels, y=data)
plt.title('Sample Bar Chart')
plt.show()
"""

map_cell_Content = """
# Code to display a map of Corvallis using Plotly with OSM style
corvallis_coords = [44.5646, -123.2620]  # Latitude and Longitude of Corvallis

fig = px.scatter_mapbox(lat=[corvallis_coords[0]], lon=[corvallis_coords[1]],
                        zoom=10,
                        mapbox_style="open-street-map")

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  title='Map of Corvallis')
fig.show()
"""


api_cell_Content = """
import requests
import pandas as pd

# Endpoint for JSONPlaceholder posts
url = "https://jsonplaceholder.typicode.com/posts"

# Fetching posts from user with id 1
params = {'userId': 1}

response = requests.get(url, params=params)
data = response.json()

# Convert the JSON data to a DataFrame and display the first few rows
if response.status_code == 200 and data:
    df = pd.DataFrame(data)
    print("First few posts from user 1:")
    display(df.head())  # Show the first few rows of the DataFrame
else:
    print("Failed to retrieve data")
"""


conclusion_Content = "print('Summary of the findings and conclusion here.')"


# Define the structure of your notebook here
cell_structure = {
    0: {"title": "Imports", "content": imports_Content, "purpose": "code"},
    1: {"title": "Executive Summary", "content": executive_Content, "purpose": "narrative"},
    2: {"title": "Chart Cell", "content": chart_cell_Content, "purpose": "code"},
    3: {"title": "Map Cell", "content": map_cell_Content, "purpose": "code"},
    4: {"title": "API Example Cell", "content": api_cell_Content, "purpose": "code"},
    5: {"title": "Conclusion", "content": conclusion_Content, "purpose": "code"}
}


# Create the notebook with the defined structure
notebook = create_notebook(cell_structure)

# Save the notebook to a file
with open("GeneratedNotebook.ipynb", "w", encoding='utf-8') as f:
    nbf.write(notebook, f)
