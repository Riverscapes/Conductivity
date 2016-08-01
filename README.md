# Conductivity Model

## Summary

Electrical conductivity has been shown to be a potential indicator of aquatic macroinvertebrate species richness (Spieles and Mitsch 2000, Brown, Hannah et al. 2007) and also can influence faunal life stages (Tarín and Cano 2000).  Preliminary GPP model development work by [Eco Logical Research, Inc.](https://sites.google.com/a/ecologicalresearch.net/ecologicalreseach-net/) (ELR) has shown promising results using temperature, solar inputs, and conductivity as inputs. By incorporating a previously developed electrical conductivity predictive regression model (Olson and Hawkins 2012), we are building an automated workflow for predicting conductivity for a stream network, summarizing predicted upstream conductivity values per ~1000 meter stream segments. 

The random forest hydraulic conductivity model was developed using 19 environmental variables (detailed in [Olson and Hawkins, 2012](http://onlinelibrary.wiley.com/doi/10.1029/2011WR011088/abstract)). To determine predicted conductivity for a stream network, we first segment streams reaches and delineate upstream catchment polygons for each stream segment end point, using the *Segment Stream Network* and *Delineate Catchments* tools in the [RCA Tools](https://github.com/jesselangdon/RCA-tools) toolbox. These catchment polygons are then used to calculate mean values from raster datasets representing each of the 19 environmental variables. The summary values for each catchment and it's associated segment record are compiled into a table, which then serves as the primary input for the random forest model to generate predicted conductivity values per segment record.  Currently, the Conductivity toolbox includes two tools: *Pre-process Environmental Parameters* and *Predict Conductivity*.

## Project Status and Updates

* 8/6/2015 - Beta version of the Pre-processing Tool, v0.1, uploaded.
* 7/25/2016 - Pre-processing tool, v0.3, uploaded.
* 7/27/2016 - New tool added to Conductivity Tools toolbox, Predict Conductivity

## Installation
Download the Conductivity Tools toolbox repository from https://github.com/jesselangdon/conductivity.git.  This will include the ArcGIS toolbox, the required Python and R scripts, and the Random Forest model (rf17bCnd9.rdata). The toolbox can then be added to ArcGIS by opening the ArcToolbox window, right-clicking ArcToolbox and choosing Add Toolbox.

## Data Input Variables and Requirements
**Pre-process Environmental Parameters** 
* *Catchment Area Feature Class* - This should be a polygon dataset representing catchment areas within the study area.  The catchment areas can be delineated using the [Catchment Tools](http://github.com/jesselangdon/catchment_tool).
* *Output Workspace* - A folder where the output table will be stored.
* *Environmental Parameters Workspace* - The 19 environmental parameters that are used by the Random Forest predictive model should be stored as raster datasets in a single directory. The file name for each raster dataset is hard-coded into the tool. These raster datasets (which are rather large) can be obtained by contacting the tool's author directly at ([jesse@southforkresearch.org)](jesse@southforkresearch.org).

**Predict Conductivity**
* *Stream Network Polyline Feature Class* - Segmented stream network polyline feature class to which predicted conductivity values will be joined.  A new dataset will be created for the output.  This dataset should include a unique identifier field called *LineOID*.
* *Environmental Parameter Table* - The table of summarized environmental parameters.  Each field store mean values for one of the 19 environmental variables required by the Random Forest conductivity prediction model.
* *Predicted Conductivity Output Feature Class* - The segmented stream network, with predicted conductivity values joined as a new attribute field.

### Automated Processing Steps
1.  Calculate mean value for each parameter per catchment polygon.
2.  Compile table with summarized environmental parameter values associated with each segment endpoint.
3.  Predict conductivity values per segment endpoint record using a random forest model.

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

The Conductivity Tools toolbox has been developed for [South Fork Research, Inc.](http://southforkresearch.org) by Jesse Langdon.\