# Conductivity Model

## Summary

Electrical conductivity has been shown to be a potential indicator of aquatic macroinvertebrate species richness (Spieles and Mitsch 2000, Brown, Hannah et al. 2007) and also can influence faunal life stages (Tarín and Cano 2000). Preliminary gross primary productivity model development work by [Eco Logical Research, Inc.](https://sites.google.com/a/ecologicalresearch.net/ecologicalreseach-net/) (ELR) has shown promising results using temperature, solar inputs, and conductivity as inputs. By incorporating a previously developed electrical conductivity predictive regression model (Olson and Hawkins 2012), we built an automated workflow for predicting conductivity for a stream network, summarizing predicted upstream conductivity values (μS cm<sup>−1</sup>) per 1000 meter stream segments.

The random forest electrical conductivity model was developed using 19 environmental parameters (detailed in [Olson and Hawkins, 2012](http://onlinelibrary.wiley.com/doi/10.1029/2011WR011088/abstract)). To determine predicted electrical conductivity for a stream network, a series of data pre-processing steps must be performed prior to initiating the actual modeling process. The user must first segment streams reaches into segments of uniform-length using the Segment Stream Network from the [Geomorphic Network and Analysis Toolbox (GNAT)](https://github.com/SouthForkResearch/gnat), a custom ArcGIS Python toolbox developed by [South Fork Research, Inc](https://southforkresearch.org). The user should then delineate upstream catchment area polygons for reach stream segment using another custom Python toolbox, the [Catchment Tool](https://github.com/SouthForkResearch/catchment-tool). These upstream catchment area polygons are used to calculate mean values from raster datasets representing each of the 19 environmental parameters. The summary values for each catchment area and it's associated stream segment are compiled into a table, which serves as the primary input for the random forest model to generate predicted electrical conductivity values per stream segment. 

Currently, **Conductivity Tools** includes two tools: *Pre-process Environmental Parameters* and *Predict Conductivity*, which should be run in sequence.

## Download

#### [Current Version (0.5.2)](https://github.com/SouthForkResearch/conductivity/archive/master.zip) released on 3/8/2017.
* Revised output Riverscapes Project XML file.

### Requirements

* Python 2.7
* R 3.2.5
* RandomForest (R package)
* Conductivity Tools
* GNAT (optional)

*Please note*: After R is installed, check that the `Rscript` command is available in your Windows command line terminal.  If not, then the R installation folder (i.e. for Windows, this would be similar to "C:\Program Files\R\R-3.2.5\bin") should be added to the system environment PATH variable. Instructions on how to do this can be found [here](http://windowsitpro.com/systems-management/how-can-i-add-new-folder-my-system-path).

### Installation

Conductivity Tools is provided as a zip file containing an ESRI .tbx file and supporting scripts.

1. Unzip the contents of the zip file to your computer. This will include the ArcGIS toolbox, the required Python and R scripts, and the Random Forest model (rf17bCnd9.rdata).
2. Open ArcGIS
2. Open the ArcToolbox window, right-click `ArcToolbox` and choose `Add Toolbox`.

## Using the Conductivity Tools

### Data Input Variables

**Pre-process Environmental Parameters** 

* *Catchment Area Feature Class* - This should be a polygon feature class representing catchment areas within the study area.  The catchment areas can be delineated using the [Catchment Tools](http://github.com/SouthForkResearch/catchment-tool).
* *Output Workspace* - A folder where the output table will be stored.
* *Environmental Parameters Workspace* - The 19 environmental parameters that are used by the Random Forest predictive model should be stored as raster datasets in a single directory. The file name for each raster dataset is hard-coded into the tool. These raster datasets (which are rather large) can be obtained by contacting the tool's author directly at ([jesse@southforkresearch.org)](jesse@southforkresearch.org).

**Predict Conductivity**

* *Stream Network Polyline Feature Class* - Segmented stream network polyline feature class to which predicted conductivity values will be joined. A new dataset will be created for the output. This dataset should include a unique identifier field called *LineOID*.
* *Environmental Parameter Table* - The table of summarized environmental parameters. Each field store mean values for one of the 19 environmental variables required by the Random Forest conductivity prediction model.
* *Predicted Conductivity Output Feature Class* - The segmented stream network, with predicted conductivity values (μS cm<sup>−1</sup>) joined as a new attribute field.
* *Output Metadata XML file* - XML file which stores metadata about the modeling process.

### Automated Processing Steps

*Pre-process Environmental Parameter*

1.  Remove catchment polygon records where error_code = 1.
2.  Calculate mean value for each environmental parameter per catchment polygon.
3.  Compile table with summarized environmental parameter values associated with each segment endpoint.

*Predict Conductivity*

4.  Predict conductivity values per segment endpoint record using a random forest model.
5.  Join predicted conductivity values back to segmented stream network polyline feature class.

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

### Citations

* Brown, L. E., et al. (2007). Vulnerability of alpine stream biodiversity to shrinking glaciers and snowpacks. Global Change Biology 13(5): 958-966.
* Liaw, A. and M. Wiener. 2002. Classification and regression by randomForest. R New 2(3): 18-22. Package URL: https://cran.r-project.org/web/packages/randomForest. Accessed 6/21/2016.
* Olson, J. R. and C. P. Hawkins (2012). Predicting natural base-flow stream water chemistry in the western United States. Water Resources Research 48(2): W02504.
* Spieles, D. J. and W. J. Mitsch (2000). "Macroinvertebrate community structure in high-and low-nutrient constructed wetlands." Wetlands 20(4): 716-729.
* R Core Team (2016). R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria. URL https://www.R-project.org/
* Tarín JJ, Cano A, editors. Fertilization in protozoa and metazoan animals: cellular and molecular aspects. Springer Science & Business Media; 2012 Dec 6.

### Acknowledgments

The Conductivity Tools toolbox has been developed for [South Fork Research, Inc.](http://southforkresearch.org) by [Jesse Langdon](https://github.com/jesselangdon).
