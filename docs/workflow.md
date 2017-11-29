### Using the Conductivity Tools

#### Data Input Variables

**Pre-process Environmental Parameters** 

* *Catchment Area Feature Class* - This should be a polygon feature class representing catchment areas within the study 
area.  The catchment areas can be delineated using the [Catchment Tools](http://github.com/SouthForkResearch/catchment-tool).
* *Output Workspace* - A folder where the output table will be stored.
* *Environmental Parameters Workspace* - The 19 environmental parameters that are used by the Random Forest predictive 
model should be stored as raster datasets in a single directory. The file name for each raster dataset is hard-coded 
into the tool. These raster datasets (which are rather large) can be obtained by contacting the tool's author directly 
at ([jesse@southforkresearch.org)](jesse@southforkresearch.org).

**Predict Conductivity**

* *Stream Network Polyline Feature Class* - Segmented stream network polyline feature class to which predicted 
conductivity values will be joined. A new dataset will be created for the output. This dataset should include a 
unique identifier field called *LineOID*.
* *Environmental Parameter Table* - The table of summarized environmental parameters. Each field store mean values 
for one of the 19 environmental variables required by the Random Forest conductivity prediction model.
* *Predicted Conductivity Output Feature Class* - The segmented stream network, with predicted conductivity values 
(μS cm<sup>−1</sup>) joined as a new attribute field.
* *Output Metadata XML file* - XML file which stores metadata about the modeling process.

#### Automated Processing Steps

*Pre-process Environmental Parameter*

1.  Remove catchment polygon records where error_code = 1.
2.  Calculate mean value for each environmental parameter per catchment polygon.
3.  Compile table with summarized environmental parameter values associated with each segment endpoint.

*Predict Conductivity*

4.  Predict conductivity values per segment endpoint record using a random forest model.
5.  Join predicted conductivity values back to segmented stream network polyline feature class.

#### Metadata

Currently the Conductivity Tools produce XML files when the tools are run in ArcGIS. These XML  files store metadata 
about the input and output parameters specified in each model run, as well as user-specified tool parameter values when 
applicable.

* **metadata_YYYYMMDD.xml** · This XML file is written by default when the second tool in the workflow – Predict 
Conductivity – is run. This file stores basic information, including start and stop times, total processing time, and 
the name and local directory locations of input and output files.
* **project.rs.xml** · This is an optional output, and is only written if the user indicates that the model run is part 
of a Riverscapes project. The project.rs.xml is more extensive then the Metadata_YYYYMMDD.xml file, and typically 
includes metadata about the spatial extent of the project, model settings, the Riverscapes project name, a “realization”
 representing the specific inputs and parameters associated with the model run, and an “analysis” which is defined by 
 the model data outputs.
