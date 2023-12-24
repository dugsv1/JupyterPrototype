import nbformat as nbf
import subprocess
import numpy as np
import os
import uuid
import shutil


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


def execute_notebook(notebook_file):
    try:
        command = [
            "jupyter", "nbconvert", "--to", "notebook",
            "--execute", "--inplace",
            "--ExecutePreprocessor.timeout=600",
            notebook_file
        ]
        subprocess.run(command, check=True)
        print(
            f"{notebook_file} has not been executed.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the notebook.")
        print(e)


def convert_notebook(notebook_file, output_file, output_format='html'):
    temp_notebook = None
    temp_image_dir = None

    # Check if conversion is needed
    if scan_for_conversion(notebook_file) and output_format == 'pdf':
        temp_notebook, temp_image_dir = preprocess_notebook(notebook_file)
        notebook_file = temp_notebook
        print("Found plots that require rendering, saving to temp folder...")
    else:
        notebook_file = notebook_file

    # Determine the conversion format (HTML or PDF)
    if output_format not in ['html', 'pdf']:
        print("Invalid output format specified. Please use 'html' or 'pdf'.")
        return

    output_file = "../docs/" + output_file + "." + output_format

    # Check if the notebook is executed
    if not is_notebook_executed(notebook_file):
        execute_notebook(notebook_file)

    # Construct the command based on the desired output format
    command = [
        "jupyter", "nbconvert",
        "--ExecutePreprocessor.timeout=600",
        f"--to={output_format}",
        "--execute", notebook_file,
        f"--output={output_file}"
    ]

    try:
        # Run the command and capture the output
        result = subprocess.run(command, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(
            f"Notebook successfully converted to {output_file}")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(
            f"An error occurred while converting the notebook to {output_format}.")
        print(e.stderr.decode())

    if temp_notebook:
        try:
            os.remove(temp_notebook)
            for image_file in os.listdir(temp_image_dir):
                try:
                    os.remove(os.path.join(temp_image_dir, image_file))
                except PermissionError as e:
                    print(f"PermissionError: {e}")
            os.rmdir(temp_image_dir)
        except PermissionError as e:
            print(f"PermissionError: {e}")


def scan_for_conversion(notebook_file):
    with open(notebook_file, 'r', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)

    return any('# ConvertToPDFImage' in cell.source for cell in nb.cells if cell.cell_type == 'code')


def is_notebook_executed(notebook_file):
    with open(notebook_file, 'r', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)

    return all('execution_count' in cell and cell.execution_count is not None for cell in nb.cells if cell.cell_type == 'code')


def preprocess_notebook(notebook_file):
    # Define the temporary image directory
    temp_image_dir = "../temp"
    # Make a Copy of the Notebook
    notebook_copy_path = f"{temp_image_dir}/temp_{uuid.uuid4()}.ipynb"
    shutil.copyfile(notebook_file, notebook_copy_path)

    os.makedirs(temp_image_dir, exist_ok=True)

    with open(notebook_copy_path, 'r+', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == 'code' and '# ConvertToPDFImage' in cell.source:
                image_filename = f"{temp_image_dir}/{uuid.uuid4()}.png"

                # Append code to the cell to save its output as an image
                capture_code = f"""
# Code appended to capture output as an image
fig.write_image('{image_filename}')  # Save the figure as an image
Image(fig.to_image(format="png"))
"""
                cell.source = cell.source.replace("fig.show()", "#fig.show()")
                cell.source += capture_code

        # Write the modified notebook back to the same file
        f.seek(0)
        f.truncate()
        nbf.write(nb, f)

    # Step 4: Execute the Modified Copy
    execute_notebook(notebook_copy_path)

    # Return the path to the temp notebook and image dir
    return notebook_copy_path, temp_image_dir


imports_Content = """
# Import necessary libraries
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from IPython.display import Image
import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go
pyo.init_notebook_mode(connected=True)
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
# Code to display a map of Corvallis with random points using Plotly with OSM style
# ConvertToPDFImage

# Sample data around Corvallis
num_points = 500
corvallis_coords = [44.5646, -123.2620]
np.random.seed(42)
lats = np.random.normal(loc=corvallis_coords[0], scale=0.01, size=num_points)
lons = np.random.normal(loc=corvallis_coords[1], scale=0.01, size=num_points)
metadata = [f"Point {i+1}" for i in range(num_points)]

# Create a scatter mapbox to display the points
fig = px.scatter_mapbox(lat=lats, lon=lons,
                        zoom=12,
                        mapbox_style="open-street-map",
                        hover_name=metadata)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  title='Map of Corvallis with Sample Points')
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


# Define the structure of your notebook
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
notebook_file = "../docs/GeneratedNotebook.ipynb"

# Save the notebook to a file
with open(notebook_file, "w", encoding='utf-8') as f:
    nbf.write(notebook, f)

# Execute and convert the notebook to HTML
convert_notebook(notebook_file, "html_output", output_format='html')
# Convert the notebook and convert it to PDF
convert_notebook(notebook_file, "pdf_output", output_format='pdf')
