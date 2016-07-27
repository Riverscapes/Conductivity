# file name:	predict_cond.py
# description:	This tool automates the process of predicting conductivity values for a stream network. Based on a table
#               of summarized model parameters (output from the Pre-process Environmental Parameters tool) , a Random Forest
#               model is applied to the parameter table using an external R script.  After R script is called, the RF
#               prediction is then joined back to the input stream network.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, built-in Python modules
# version:		0.1

import arcpy
import subprocess
import os.path
import gc

inFC = arcpy.GetParameterAsText(0) # stream network polyline feature class (i.e. segments)
inParams = arcpy.GetParameterAsText(1) # filepath to the dbf file with summarized parameters ( i.e. ws_cond_param.dbf)
outFC = arcpy.GetParameterAsText(2) # stream network polyline feature class, with predicted conductivity

def main(inFC, inParams, outFC):
    arcpy.AddMessage("Predicting conductivity using Random Forest model in R...")
    gc.enable() # turn on automatic garbage collection
    outDir = os.path.dirname(outFC) # get output directory path

    # variables for the subprocess function
    pathName = os.path.dirname(os.path.abspath(__file__))
    scriptName = 'condRF.R'
    modelName = 'rf17bCnd9.rdata'
    scriptPath = os.path.join(pathName, scriptName)
    modelPath = os.path.join(pathName, modelName)

    argR = [modelPath, outDir, inParams] # list of arguments that will be passed to condRF.R script

    cmd = ['Rscript', scriptPath] + argR # construct the R command line argument

    # send the command to the predict_conductivity.r script
    process = subprocess.Popen(cmd, universal_newlines=True, shell=True)
    process.wait()

    # the predictive output as a csv, for joining to the stream segments feature class
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

    # turn off automatic garbage collection
    gc.disable()

    arcpy.AddMessage("Conductivity prediction process complete!")
    return

if __name__ == "__main__":
    main(inFC, inParams, outFC)