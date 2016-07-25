import arcpy
import subprocess
import os.path

# inFC = arcpy.GetParameterAsText(0) # polyline feature class (i.e. segments)
# inParams = arcpy.GetParameterAsText(1) # filepath to the dbf file with summarized parameters ( i.e. ws_cond_param.dbf)
# outDir = arcpy.GetParameterAsText(2) # output directory where the final shapefile will be stored
inFC = r"C:\JL\Testing\Conductivity\HUC6\inputs\catch_final.shp"
inParams = r"C:\JL\Testing\Conductivity\HUC6\outputs\ws_cond_param_20160721.dbf"
outDir = r"C:\JL\Testing\Conductivity\HUC6\outputs"

def main(inFC, inParams, outDir):
    arcpy.AddMessage("Predicting conductivity using Random Forest model in R...")
    # variables for the subprocess function
    pathName = os.path.dirname(os.path.abspath(__file__))
    # pathName = r"C:\dev\conductivity"
    scriptName = 'condRF.R'
    modelName = 'rf17bCnd9.rdata'
    scriptPath = os.path.join(pathName, scriptName)
    modelPath = os.path.join(pathName, modelName)

    # list of arguments that will be passed to condRF.R script
    argR = [modelPath, outDir, inParams]

    # construct the R command line argument
    cmd = ['Rscript', scriptPath] + argR

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
    arcpy.AddMessage("Exporting final feature class as " + outDir + r"\final_pred_cond.shp...")
    arcpy.CopyFeatures_management("joinFC_lyr", outDir + r"\final_pred_cond.shp")
    return

if __name__ == "__main__":
    main(inFC, inParams, outDir)