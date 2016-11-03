# file name:	predict_cond.py
# description:	This tool automates the process of predicting conductivity values for a stream network. Based on a table
#               of summarized model parameters (output from the Pre-process Environmental Parameters tool) , a Random Forest
#               (RF) model is applied to the parameter table using an external R script.  After the R script is called, the
#               RF prediction is then joined back to the input stream network.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, built-in Python modules
# version:		0.2

import arcpy
import subprocess
import os.path
import sys
import gc
import metadata

inFC = arcpy.GetParameterAsText(0) # stream network polyline feature class (i.e. segments)
inParams = arcpy.GetParameterAsText(1) # filepath to the dbf file with summarized parameters ( i.e. ws_cond_param.dbf)
outFC = arcpy.GetParameterAsText(2) # stream network polyline feature class, with predicted conductivity
outMeta = arcpy.GetParameterAsText(3) # metadata XML file

def checkLineOID(inFC):
    """Checks the input upstream catchment area polygon feature class for the
    presence of an attribute field named 'LineOID'.

    Args:
        inFC: Input upstream catchment area polygon feature class

    Returns:
        A boolean true or false value.
    """
    fieldName = "LineOID"
    fields = arcpy.ListFields(inFC, fieldName)
    for field in fields:
        if field.name == fieldName:
            return True
        else:
            return False


def main(inFC, inParams, outFC, outMeta):
    """Main processing function for the Predict Conductivity tool.

    Args:
        inFC: Input stream network polyline feature class
        inParams: table of summarized model parameter values
        outFC: Output stream network polyline feature class, with predicted
        conductivity values joined as new attribute fields.
    """

    if checkLineOID(inFC) == True:
        arcpy.AddMessage("Predicting conductivity using Random Forest model in R...")
        gc.enable() # turn on automatic garbage collection
        outDir = os.path.dirname(outFC) # get output directory path

        # start writing metadata
        mWriter = metadata.MetadataWriter("Predict Conductivity Tool", "0.2")
        mWriter.createRun()
        mWriter.currentRun.addParameter("Stream Network Polyline Feature Class", inFC)
        mWriter.currentRun.addParameter("Environmental Parameter Table", inParams)
        mWriter.currentRun.addOutput("Predicted Conductivity Output Feature Class", outFC)

        # variables for the subprocess function
        #pathName = os.path.dirname(os.path.abspath(__file__)) # filepath for the predict_cond.py file
        scriptPathName = os.path.realpath(__file__)
        pathName = os.path.dirname(scriptPathName)
        scriptName = 'condRF.R'
        modelName = 'rf17bCnd9.rdata'
        rScriptPath = os.path.join(pathName, scriptName)
        modelPath = os.path.join(pathName, modelName)

        argR = [modelPath, outDir, inParams] # list of arguments for condRF.R script

        cmd = ['Rscript', rScriptPath] + argR # construct R command line argument

        # send command to predict_conductivity.r
        process = subprocess.Popen(cmd, universal_newlines=True, shell=True)
        process.wait()

        # predictive output
        predictedCondCSV = outDir + "\\predicted_cond.csv"
        arcpy.TableToTable_conversion(predictedCondCSV, outDir, r"predicted_cond.dbf")

        # join conductivity predictive output to stream segment feature class
        arcpy.AddMessage("Joining predicted conductivity results to the stream network...")
        arcpy.MakeTableView_management(outDir + r"\predicted_cond.dbf", "predicted_cond_view")
        arcpy.MakeFeatureLayer_management(inFC, "inFC_lyr")
        arcpy.FeatureClassToFeatureClass_conversion("inFC_lyr", r"in_memory", "inFC_tmp")
        arcpy.JoinField_management(r"in_memory\inFC_tmp", "LineOID", "predicted_cond_view", "LineOID")
        arcpy.MakeFeatureLayer_management(r"in_memory\inFC_tmp", "joinFC_lyr")
        arcpy.AddMessage("Exporting final feature class as " + outFC)
        arcpy.CopyFeatures_management("joinFC_lyr", outFC)

        # clean up temporary files
        arcpy.Delete_management(outDir + r"\predicted_cond.dbf")
        arcpy.Delete_management(outDir + r"\predicted_cond.csv")
        gc.disable()

        # finalize and write metadata file
        strToolStatus = "Success"
        mWriter.finalizeRun(strToolStatus)
        mWriter.writeMetadataFile(outMeta)

        arcpy.AddMessage("Conductivity prediction process complete!")
    else:
        arcpy.AddMessage("The LineOID attribute field is missing! Cancelling process...")
        sys.exit(0) # terminate process
    return

#TESTING
inFC = r"C:\JL\Projects\conductivity\Entiat\_1Sources\segments_1000m_20160930.gdb\segments1000"
inParams = r"C:\JL\Projects\conductivity\Entiat\_2Model\ws_cond_param.dbf"
outFC = r"C:\JL\Projects\conductivity\Entiat\_2Model\conductivity_entiat_20161103.shp"
outMeta = r"C:\JL\Projects\conductivity\Entiat\_2Model\metadata_20161103.xml"

if __name__ == "__main__":
    main(inFC, inParams, outFC, outMeta)