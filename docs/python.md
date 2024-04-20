## Installing with Anaconda (miniconda)

`rillgen2d' graphic user interface (GUI) is built in Python with Streamlit. 

We use [Anaconda](https://docs.conda.io/en/latest/){target=_blank} with [miniconda](https://docs.anaconda.com/free/miniconda/index.html){target=_blank} to build our environment with all of the necessary dependencies. We recommend using the [`mamba`](https://github.com/mamba-org/mamba){target=_blank} solver for faster installation over `conda`.

We have provided three `environment.yml` files which can be used with [conda](https://docs.conda.io/en/latest/){target=_blank} to install Python environment on Linux (Ubuntu), Mac OS X, or Windows 10.

Example install using `conda` and `mamba`:

```bash
# update conda
conda update -n base -c defaults conda

# create new environment for rillgen2d
mamba env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
```

to remove or update:

```bash
# check your python version (should be 3.11.*)
python --version

# remove old rillgen2d environment
conda remove --name rillgen2d --all

# update conda environment 
mamba env update --prefix ./env --file environment_linux.yml  --prune
```

### Starting the GUI

Once the `rillgen2d` Python environment has been created, you can start the Streamlit GUI:

```
# start the Streamlit UI
python run.py
```

## Developer Documentation

This document provides an overview of the Python files within this project and their respective functionalities.

## 1. `rillgen2d.py`

This file contains the core logic of the Rillgen2d application. It defines the `Rillgen2d` class, which acts as a process and manages the execution of the rill generation model. 

**Key Components:**

*   **`Rillgen2d` class:**
    *   Handles input parameters, file paths, and temporary directory management.
    *   Implements methods for:
        *   Converting GeoTIFF images to text format.
        *   Setting up and running the rillgen C library.
        *   Generating hillshade and color relief images.
        *   Setting georeferencing information for output files.
        *   Generating a Leaflet Folium map with interactive layers.
        *   Saving output data.
    *   Utilizes GDAL and subprocesses to interact with geospatial data and external tools.

*   **Helper functions:**
    *   `function_decorator`: Wraps functions to handle exceptions and log messages.
    *   `GetExtent`, `ReprojectCoords`: Assist with geospatial calculations. 
    *   `convert_ppm`: Converts PPM files to PNG for map display.

## 2. `parameters.py`

This file defines the `Parameters` class, responsible for managing the input parameters of the Rillgen2d model. 

**Key Features:**

*   **Parameter fields:** Defines various types of input fields using subclasses of the `Field` class (e.g., `NumericField`, `FileField`, `OptionField`).
*   **Validation:** Implements validation logic to ensure parameter values are within acceptable ranges or formats.
*   **File I/O:** Handles loading parameter values from a file and saving them for later use.
*   **UI Integration:** Provides methods for drawing the parameter UI elements using Streamlit. 

## 3. `frontend.py`

This file implements the Streamlit application frontend, providing the user interface for interacting with Rillgen2d.

**Key Functionalities:**

*   **UI Tabs:** Creates tabs for "Parameters" and "User Manual."
*   **Parameter Input:** 
    *   Allows users to input DEM files via URL or local upload.
    *   Provides interactive widgets for adjusting model parameters.
    *   Handles parameter validation and error messages.
*   **Execution Control:** 
    *   Starts and stops the Rillgen2d process.
    *   Displays the console output for monitoring progress.
*   **Output Visualization:** 
    *   Displays a preview of the input DEM.
    *   Renders the generated map with interactive layers (hillshade, rills, tau).
    *   Provides options for saving the output data.

## 4. `utils.py`

This file contains utility functions used by other parts of the application.

**Included Utilities:**

*   `get_image_from_url`: Downloads a GeoTIFF image from a given URL.
*   `extract_geotiff_from_tarfile`: Extracts a GeoTIFF image from a tarfile.
*   `open_file_dialog`: Opens a file dialog to allow users to select a local file.
*   `reset_session_state`: Clears the Streamlit session state.

## 5. Documentation for `fields.py`

The `fields.py` file defines the base classes and specific implementations for handling input parameters within the Rillgen2d application. It provides a framework for creating and managing various types of input fields with functionalities like UI rendering, validation, and value retrieval.

### Core Concepts:

*   **`Field` Abstract Class:** Defines the basic interface for all parameter field types. Subclasses must implement methods for drawing UI elements, obtaining values, and validating user inputs. 
*   **`BaseField` Data Class:** Provides a common structure for storing field attributes like name, display name, help text, comment, and value. 
*   **Specific Field Classes:** 
    *   `EmptyField`: A placeholder field without any UI representation or value.
    *   `OptionField`: Creates a dropdown selection box with a list of options. Allows conditional rendering of additional fields based on the selected option.
    *   `CheckBoxField`: Represents a checkbox with optional conditional fields that appear when checked.
    *   `FileField`: Enables users to upload files and stores the file path as the field value.
    *   `NumericField`: Provides a numeric input field with options for step size and display format.
    *   `StaticParameter`: Represents a static parameter without any UI interaction. Stores a fixed value.

### Functionality:

*   **UI Rendering:** Each specific field class implements a `draw` method to render the appropriate UI element using Streamlit.
*   **Value Retrieval:** The `get_value` method is used to obtain the current value of the field.
*   **Validation:** The `validate` method checks the field value for errors and returns an error message if invalid.
*   **Conditional Fields:** `OptionField` and `CheckBoxField` support conditional rendering of additional fields based on the selected option or checkbox state. 

### Usage:

The field classes are used within the `Parameters` class in `parameters.py` to define the input parameters for the Rillgen2d model. Each parameter is represented by an instance of a specific field class, allowing for a flexible and modular approach to parameter management.

## Summary

These four Python files work together to provide a user-friendly interface for running the Rillgen2d model, visualizing its outputs, and managing its parameters. The code utilizes libraries like GDAL, Streamlit, and Folium to interact with geospatial data, build interactive visualizations, and create a user-friendly interface.