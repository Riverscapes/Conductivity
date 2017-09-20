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