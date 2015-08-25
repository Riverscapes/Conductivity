# Conductivity Model

## Summary

Electrical conductivity has been shown to be a potential indicator of aquatic macroinvertebrate species richness (Spieles and Mitsch 2000, Brown, Hannah et al. 2007) and also can influence faunal life stages (Tarín and Cano 2000).  Preliminary GPP model development work by [Eco Logical Research, Inc.](https://sites.google.com/a/ecologicalresearch.net/ecologicalreseach-net/) (ELR) has shown promising results using temperature, solar inputs, and conductivity as inputs. By incorporating a previously developed electrical conductivity predictive regression model (Olson and Hawkins 2012), we are building an automated workflow for predicting conductivity for a stream network, summarizing predicted upstream conductivity values per ~1000 meter stream segments. 

The random forest hydraulic conductivity model was developed using 19 environmental variables (detailed in [Olson and Hawkins, 2012](http://onlinelibrary.wiley.com/doi/10.1029/2011WR011088/abstract)).  To determine predicted conductivity for each stream segment, we first delineate upstream catchment polygons for each stream segment end point, using the [Segment](http://github.com/jesselangdon/segment_tool) and [Catchment Tools](http://github.com/jesselangdon/catchment_tool). These catchment polygons are then used to calculate mean values from raster datasets representing each of the 19 environmental variables.  The summary values for each catchment and it's associated segment record are then compiled into a table, which then serves as the primary input for the random forest model to generate predicted conductivity values per segment record.  Currently, this tool does not include incorporate Random Forest predictive modeling process. The sole purpose of the tool is preparing data that will serve as inputs for this model.

## Project Status and Updates

* Predictive conductivity model has been completed for the Middle Fork John Day and Entiat basins.  Originally, data pre-processing was performed by a stand-alone script in Spatial Ecology's [Geospatial Modeling Environment](http://www.spatialecology.com/gme/) (GME), and conductivity was predicted using the conductivity model (built as a Random Forest object) in R. South Fork Research has ported the data pre-processing workflow from GME to Python.  
* 8/6/2015 - Beta version of the Conductivity Pre-processing Tool, v0.1, uploaded.

## Installation
Download the Conductivity Tools toolbox file (Conductivity Tools.tbx) and python file (polystat_cond.py), and store it locally in the same folder.  Import the toolbox into ArcMap (version 10.1 or higher).

## Data Input Variables and Requirements
* *Catchment Area Feature Class* - This should be a polygon dataset representing catchment areas within the study area.  The catchment areas can be delineated using the [Catchment Tools](http://github.com/jesselangdon/catchment_tool).
* *Output Workspace* - A folder where the output table will be stored.
* *Environmental Parameters Workspace* - The 19 environmental parameters that are used by the Random Forest predictive model should be stored as raster datasets in a single directory. The file name for each raster dataset is hard-coded into the tool. These raster datasets can be obtained by contacting the tool's author directly at ([jesse@southforkresearch.org)](jesse@southforkresearch.org).

### Method Workflow
1.  Calculate mean value for each parameter per catchment polygon.
2.  Compile table with summarized environmental parameter values associated with each segment endpoint.
3.  Predict conductivity values per segment endpoint record using random forest model (_Currently, this step must be performed in an R environment_).

#### Environmental parameters used by the Random Forest model to predict conductivity:
* Atmospheric Ca
* Atmospheric Mg
* Atmospheric SO4
* Compressive strength
* Day last freeze
* Log hydraulic condition
* Max wet days
* Maximum temperature
* Mean maximum EVI
* Mean precipitation
* Mean summer precipitation
* Mean wet days
* Minimum precipitation
* Percent CaO
* Percent MgO
* Percent S
* Soil bulk density
* Soil erodibility
* Soil permeability

## Acknowledgments

The Conductivity pre-processing tool is developed by Jesse Langdon, [South Fork Research, Inc.](http://southforkresearch.org) (SFR).
