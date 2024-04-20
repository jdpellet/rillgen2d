## User Interface

### Interface Overview:

The Rillgen2d interface consists of two tabs:

*   **Parameters:** This tab allows you to input a DEM file, adjust model parameters, and control the execution of the simulation.
*   **User Manual:** Provides detailed information about the model, parameters, and interpretation of results.

### Running a Simulation:

1. **Input DEM:** 
    *   **Web URL:** Enter the URL of a GeoTIFF DEM file hosted online.
    *   **Local File:** Upload a GeoTIFF DEM file from your local machine.
2. **Generate Parameters:** Click the "Generate Parameters" button to read the DEM and populate the parameter fields.
3. **Adjust Parameters:** 
    *   Review the default parameter values and modify them as needed based on your specific case and the information available in the User Manual.
    *   Parameters are organized into sections for model mode, routing methods, erosion properties, and hydrologic and numerical settings.
4. **Run Rillgen2d:** Click the "Run Rillgen2d" button to start the simulation.
5. **Monitor Progress:** The console output will display progress messages and any errors that occur. 
6. **View Outputs:**
    *   **Preview:** A hillshade image of the input DEM will be displayed for visual inspection.
    *   **Map:** An interactive map with layers for hillshade, rills, and tau (shear stress) will be generated. You can toggle layers and zoom in/out to explore the results.
7. **Save Output:** Click the "Save Output" button to save the generated files (map, images, parameter settings) to a timestamped folder.

### Additional Tips:

*   Refer to the User Manual for detailed explanations of the parameters and their implications.
*   Experiment with different parameter settings to understand their effects on the model outputs.
*   Consider the limitations of the model and the uncertainties associated with the input data and parameters.

**By following these steps and referring to the available documentation, you can effectively use the Rillgen2d Streamlit application to analyze rill erosion potential and gain insights into landscape processes.**


## Input Parameters

## Input Parameters for `rillgen.c`

The `input.txt` file provides the necessary parameters for configuring and running the Rillgen2d model. Each line in the file specifies a parameter name, its value, and a brief description. Here's a breakdown of the parameters:

**1. Model Mode and Routing:**

*   `flagformode`: Determines the model mode:
    *   0: Static uniform rainfall with simple outputs (calculates factor of safety and rock thickness ratios).
    *   1: Rainfall variable in space and/or time with complex outputs (simulates rill erosion and sediment yield).
*   `flagforroutingmethod`: Specifies the flow routing method:
    *   0: Multiple Flow Direction (MFD)
    *   1: Depth-based routing 
    *   2: D-infinity

**2. Shear Stress and Erosion Parameters:**

*   `flagforshearstressequation`: Selects the equation for calculating critical shear stress of rock armor:
    *   0: Haws and Erickson (2020) equation
    *   1: Pelletier et al. (in press) equation
*   `flagformask`: Indicates whether a mask is used to define the active modeling area:
    *   0: No mask (entire DEM is considered)
    *   1: Mask provided (cells with mask value 0 are ignored)
*   `flagfortaucsoilandveg`: Specifies whether a raster for soil and vegetation critical shear stress is used:
    *   0: Fixed value (`taucsoilandvegfixed`) is applied
    *   1: Raster file provides spatially varying values
*   `flagford50`: Controls the use of a raster for rock armor median diameter (d50):
    *   0: Fixed value (`d50fixed`) is applied
    *   1: Raster file provides spatially varying d50 values
*   `flagforrockthickness`: Determines if a raster for rock armor thickness is used:
    *   0: Fixed value (`rockthicknessfixed`) is applied
    *   1: Raster file provides spatially varying thickness
*   `flagforrockcover`: Indicates whether a raster for rock armor cover fraction is used:
    *   0: Fixed value (`rockcoverfixed`) is applied
    *   1: Raster file provides spatially varying cover fraction

**3. Hydrologic and Numerical Parameters:**

*   `fillincrement`: Increment (in meters) used to raise the elevation of pits and flats during hydrologic correction. 
*   `minslope`: Minimum slope (m/m) considered for flow routing and calculations. 
*   `expansion`: Number of pixels to expand the zone of rill influence in the output.
*   `yellowthreshold`: Threshold value for the factor of safety (f) below which cells are considered potentially prone to rilling.
*   `lattice_size_x`, `lattice_size_y`: Dimensions of the DEM grid (number of columns and rows).
*   `deltax`: Cell size or resolution of the DEM (in meters).
*   `nodatavalue`: Value in the DEM that represents no data.
*   `smoothinglength`: Size of the moving window (in pixels) used for slope smoothing. 
*   `manningsn`: Manning's roughness coefficient for flow calculations.
*   `depthweightfactor`: Weighting factor used in the depth-based routing scheme.
*   `numberofslices`: Number of slices used in the depth-based routing iteration.
*   `numberofsweeps`: Number of sweeps or iterations for the entire depth-based routing process.

**4. Rainfall and Rill Properties:**

*   `rainfixed`: Fixed rainfall intensity (mm/hr) used in the static mode.
*   `taucsoilandvegfixed`: Fixed value for the critical shear stress of soil and vegetation (Pa) when not using a raster.
*   `d50fixed`: Fixed value for the median rock armor diameter (m) when not using a raster.
*   `rockthicknessfixed`: Fixed value for rock armor thickness (m) when not using a raster. 
*   `rockcoverfixed`: Fixed value for rock cover fraction when not using a raster.
*   `tanangleofinternalfriction`: Tangent of the angle of internal friction for the soil.
*   `b`, `c`: Coefficients used in the equation relating discharge to contributing area. 
*   `rillwidthcoefficient`, `rillwidthexponent`: Coefficients used to calculate rill width based on discharge. 

**These parameters control various aspects of the Rillgen2d model, including the simulation mode, flow routing method, erosion processes, and physical properties of the landscape and rainfall. Understanding these parameters is crucial for effectively using and interpreting the model outputs.**