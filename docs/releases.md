### Releases

#### [Current Version (0.5.4)](https://github.com/SouthForkResearch/conductivity/archive/master.zip) 
released on 3/27/2017.
* Revised output Riverscapes Project XML file.

### Requirements

* Python 2.7
* R 3.2.5
* RandomForest (R package)
* Conductivity Tools
* GNAT (optional)

*Please note*: After R is installed, check that the `Rscript` command is available in your Windows 
command line terminal.  If not, then the R installation folder (i.e. for Windows, this would be similar 
to "C:\Program Files\R\R-3.2.5\bin") should be added to the system environment PATH variable. 
Instructions on how to do this can be found [here](http://windowsitpro.com/systems-management/how-can-i-add-new-folder-my-system-path).

### Installation

Conductivity Tools is provided as a zip file containing an ESRI .tbx file and supporting scripts.

1. Unzip the contents of the zip file to your computer. This will include the ArcGIS toolbox, the 
required Python and R scripts, and the Random Forest model (rf17bCnd9.rdata).
2. Open ArcGIS
2. Open the ArcToolbox window, right-click `ArcToolbox` and choose `Add Toolbox`.