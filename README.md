# Conductivity Model

## Summary

Electrical conductivity has been shown to be a potential indicator of aquatic macroinvertebrate species richness (Spieles and Mitsch 2000, Brown, Hannah et al. 2007) and also can influence faunal life stages (Tarín and Cano 2000).  Preliminary GPP model development work by [Eco Logical Research, Inc.](https://sites.google.com/a/ecologicalresearch.net/ecologicalreseach-net/) (ELR) has shown promising results using temperature, solar inputs, and conductivity as inputs. By incorporating a previously developed electrical conductivity predictive regression model (Olson and Hawkins 2012), we are building an automated workflow for predicting conductivity for a stream network, summarizing predicted upstream conductivity values per ~1000 meter stream segments. 

The random forest hydraulic conductivity model was developed using 19 environmental variables (detailed in Olson and Hawkins 2012).  To determine predicted conductivity for each stream segment, we first delineate upstream catchment polygons for each stream segment end point, using the [Segment](http://github.com/jesselangdon/segment_tool) and [Catchment Tools](http://github.com/jesselangdon/catchment_tool).  These catchment polygons are then used to calculate mean values for from raster datasets representing each of the 19 environmental variables.  The summary values for each catchment and it's associated segment record are then compiled into a table, which is then serves as the primary input for the random forest model to generate predicted conductivity values per segment record.

## Project Status and Updates

* Predictive conductivity model has been completed for the Middle Fork John Day and Entiat basins.  Currently, data pre-processing is performed by a stand-alone script in Spatial Ecology's [Geospatial Modeling Environment](http://www.spatialecology.com/gme/) (GME), and conductivity is predicted using ELR's conductivity model (built as a Random Forest object) in R.  South Fork Research is in the process of porting the data pre-processing workflow from GME to Python.  
* Once a working version of the Python data pre-processing tool is available, it will be uploaded and made available on this repository.

### Method Workflow
1. Clip DEM and flowlines to HUC 4 polygon
2. Split flowlines into 200 meter segments
3. If segment length is < 25% of 200 meters, merge with adjacent segment (if from same parent stream unit)
4. Create segment end points dataset.
5. Convert stream network (and optionally, bankfull polygons) to a raster file format.
6. “Burn in” raster version of stream network using decay function equation.
7. Fill all sinks and depressions
8. Calculate flow direction
9. Calculate flow accumulation
8. Snap segment endpoints (within a 20m buffer) to grid cells with highest flow accumulation.
9. Delineate catchments using each stream segment endpoint as a pour point.
10.  Calculate mean value for each parameter per catchment polygon.
11.  Compile table with summarized environmental parameter values associated with each segment endpoint.
12.  Predict conductivity values per segment endpoint record using random forest model.

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

The GME data pre-processing script and conductivity predictive model was originally developed Dr. Carl Saunders (ELR).  The current Python version of the pre-processing tool is being developed by Jesse Langdon, [South Fork Research, Inc.](http://southforkresearch.org) (SFR).
