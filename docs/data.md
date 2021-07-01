## Local files

Rillgen2D will run on GeoTiff (.tif) images with coordinate reference system (CRS) metadata. Rasters that are missing or have no projection will not use a CRS.

You can select from your local computer any \*.tif file using the `Upload a file` button.

## Download files from URL

Users can also select URLs from public elevation datasets such as those from [OpenTopography.org](https://opentopography.org) jobs.

Results files from URL can be in either \*.tif or in \*.tar.gz (compressed) format. Rillgen2d will unzip the \*.tif file from the tarball. 


## Best Practices

### Raster sizes

In general, the larger the file, the longer it will take to process it. Rillgen2d does use some multi-threading capability to process data, but some steps are single threaded and can take a significant amount of time to run.

Rasters up to 50,000 x 50,000 pixels have been successfully tested on RillGen2D on large Linux workstations.

### Hydrological corrections

Running the hydrological correction for pit filling will add time to your model run.
