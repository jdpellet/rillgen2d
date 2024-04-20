
## Compling `rillgen.c`

Rillgen2D is written in `C`

The code is compiled by the Python script when the program is run.

To compile the `C` code outside of python, you can use `gcc` in Linux or Mac OS X

```
gcc -Wall -shared -fPIC rillgen2d.c -o rillgen2d.so
```

To compile the `C` code outside of Python on Windows 10:

```
gcc -o rillgen2d.exe rillgen2d.c
```

## Developer Documentation

## Understanding the `rillgen.c` Code

The provided `rillgen.c` code implements the core logic of the Rillgen2d model, which simulates rill erosion processes on a digital elevation model (DEM). The code is quite complex and involves various algorithms and calculations. Here's a breakdown of its key components:

**1. Data Structures and Initialization:**

*   **Grids and Variables:** The code defines several 2D grids (matrices) to store information such as topography (`topo`), slope (`slope`), rainfall (`rain`), contributing area (`area`), discharge (`discharge`), depth (`depth`), incised depth (`inciseddepth`), erosion (`eroded`), shear stress (`tau`), maximum shear stress (`maxtau`), flow direction (`angle`), and various factors used in calculations.
*   **Input Parameters:** Parameters such as flags for different model options, grid dimensions (`lattice_size_x`, `lattice_size_y`), cell size (`deltax`), Manning's n (`manningsn`), and various coefficients are read from the `input.txt` file.
*   **Neighboring Cells:** The `setupgridneighbors` function defines arrays to efficiently access neighboring cells in the grid. 

**2. Hydrologic Correction (Priority-Flood):**

*   **`priority_flood_epsilon` Function:** Implements a priority-flood algorithm to fill pits and flats in the DEM, ensuring proper drainage for subsequent calculations. 
*   **Priority Queue:** The algorithm utilizes a priority queue to efficiently process cells based on their elevation. 
*   **Epsilon Filling:** Cells identified as pits or flats are filled by incrementally raising their elevation (`fillincrement`) until they drain to a lower neighbor.

**3. Slope Calculation and Smoothing:**

*   **`calculateslope` Function:** Calculates the slope at each cell using a central difference scheme and determines the flow direction based on the steepest descent.
*   **`smoothslope` Function:** Optionally smooths the calculated slope using a moving window average to reduce the impact of noise or artifacts in the DEM.

**4. Flow Routing:**

*   **Routing Options:** The code supports three flow routing methods: Multiple Flow Direction (MFD), D-infinity, and a depth-based approach. The chosen method is determined by the `flagforroutingmethod` parameter.
*   **MFD Routing:** 
    *   `mfdflowrouteorig`, `mfdroutefordischarge` functions: Distribute flow from each cell to its downhill neighbors based on the steepest descent and a weighting factor determined by the elevation difference. 
*   **D-infinity Routing:**
    *   `dinfflowrouteorig` function: Determines the flow direction based on the steepest slope within eight possible directions and distributes flow accordingly.
*   **Depth-Based Routing:**
    *   `initialguessforrouting`, `calculatedischargefluxes`, `routing` functions: Iteratively solve for flow depths and discharge using the Manning's equation and the MFD routing scheme, updating the topography until convergence is reached. 

**5. Rill Erosion and Shear Stress Calculation:**

*   **`calculatedischarge` Function:** Calculates the discharge at each cell based on the chosen routing method and the contributing area.
*   **Shear Stress:** Calculates the shear stress exerted by the flow at each cell, considering the slope, discharge, and rill width. 
*   **Critical Shear Stress:** Determines the critical shear stress for soil and rock armor layers based on input parameters and empirical equations.
*   **Rill Erodibility:** In the dynamic mode, the code simulates rill erosion over multiple time steps, calculating the incision depth and sediment yield based on the excess shear stress and rill erodibility parameters.

**6. Output Generation:**

*   **`f1.txt`, `f2.txt`:** Store the factor of safety against rill initiation and the ratio of rock thickness to flow depth, respectively.
*   **`tau.txt`:** Stores the maximum shear stress experienced at each cell.
*   **`rills.ppm`:** Generates a PPM image visualizing the spatial distribution of rill erosion potential. 
*   **`inciseddepth.txt` (Dynamic Mode):** Stores the cumulative incision depth due to rill erosion at each cell.

**In summary, the `rillgen.c` code implements a complex model for simulating rill erosion processes on a DEM. It involves hydrologic correction, slope analysis, flow routing, shear stress calculations, and erosion modeling to predict the locations and intensity of rill development.**