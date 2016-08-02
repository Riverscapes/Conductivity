# file name:	polystat_cond.py
# description:	This tool is a derivation of the PolyStat tool, but it has been refactored to work specifically  
#				for the Conductivity model.  The tool calculates the mean value of 19 environmental parameters  
#	            (raster datasets) per polygon (in this case, upstream catchment areas), and adds that value to a  
#				field in the polygon's attribute table.  The resulting attribute table can then serve as an input 
#				to the Olson et. al. Random Forest conductivity model.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.3

import time, gc, sys, arcpy
from arcpy.sa import *
from time import strftime

# start processing time
startTime = time.time()
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("Processing started at " + str(printTime))
arcpy.AddMessage("------------------------------------")

arcpy.env.overwriteOutput = True

# check out Spatial Analyst
arcpy.CheckOutExtension("Spatial")

# input variables:
# calc_ply = arcpy.GetParameterAsText(0) # polygon feature class (i.e. catchments)
# outDir = arcpy.GetParameterAsText(1) # directory location for the polygon feature class output
# envDir = arcpy.GetParameterAsText(2) # directory containing the conductivity model raster inputs
calc_ply = r"C:\JL\Testing\Conductivity\HUC6\inputs\catch_finalCopy.shp"
outDir = r"C:\JL\Testing\Conductivity\HUC6\outputs_20160802"
envDir = r"C:\JL\ISEMP\Data\ec\model\Grids_rsmp"

param_list = [["AtmCa", "ca_avg_250"], # list of model parameter names and associated raster dataset names
            ["CaO_Mean", "cao_19jan10"],
            ["EVI_MaxAve", "evi_max_10y"],
            ["LST32AVE", "lst32f_usgs"],
            ["MAXWD_WS", "maxwd_usgs"],
            ["MEANP_WS", "meanp_usgs"],
            ["AtmMg", "mg_avg_250"],
            ["MgO_Mean", "mgo_19jan10"],
            ["MINP_WS", "minp_usgs"],
            ["AtmSO4", "so4_avg_250"],
            ["TMAX_WS", "tmax_usgs"],
            ["SumAve_P", "sumave_p"],
            ["XWD_WS", "xwd_usgs"],
            ["BDH_AVE", "bdh_usgs"],
            ["KFCT_AVE", "kfact_usgs"],
            ["LPREM_mean", "lperm_2feb10"],
            ["PRMH_AVE", "permh_usgs"],
            ["S_Mean", "s_23aug10"],
            ["UCS_Mean", "ucs_19jan10"]]

def checkLineOID(inFC):
    fieldName = "LineOID"
    fields = arcpy.ListFields(inFC, fieldName)
    for field in fields:
        if field.name == fieldName:
            return True
        else:
            return False

def addParamFields(inFC, inParam):
    # prepare the input feature class by stripping all unnecessary fields and adding in blank model parameter fields
    arcpy.AddMessage("Preparing parameter fields in " + inFC + "...")
    gc.enable()
    tmpFC = arcpy.FeatureClassToFeatureClass_conversion(inFC, "in_memory", "tmp_fc")
    field_obj_list = arcpy.ListFields(tmpFC)
    field_name_list = []
    if checkLineOID(inFC) == True:
        for f in field_obj_list:
            if not f.type == "Geometry" and not f.type == "OID" and not f.name == "LineOID":
                field_name_list.append(str(f.name))
        arcpy.DeleteField_management(tmpFC, field_name_list)
        for p in inParam:
            arcpy.AddField_management(tmpFC, p[0], "DOUBLE")
    else:
        arcpy.AddMessage("The LineOID attribute field is missing! Cancelling process...")
        sys.exit(0) # terminate process
    return tmpFC

def calcParams(inFC, inParam):
    # build an attribute table for the input fc that will include an attribute field for each parameter with summarized values
    arcpy.AddMessage("Summarizing parameter values per catchment area polygon...")
    with arcpy.da.SearchCursor(inFC, ["LineOID"]) as cursor:
        for row in cursor:
            expr = """ "LineOID" = """ + str(row[0])
            arcpy.MakeFeatureLayer_management(inFC, "tmpFC")
            arcpy.SelectLayerByAttribute_management("tmpFC", "NEW_SELECTION", expr)
            ras_record = arcpy.PolygonToRaster_conversion("tmpFC", "LineOID", "in_memory\\ras_record",
                                                          "CELL_CENTER", "#", 30)
            arcpy.AddField_management(ras_record, "LineOID", "LONG")
            arcpy.CalculateField_management(ras_record, "LineOID", "!Value!", "PYTHON_9.3")
            arcpy.CalculateStatistics_management(ras_record)
            for r in inParam:
                field_name = r[0]
                ras_name = envDir + "\\" + r[1]
                zstat_result = "in_memory\\zstat_result"
                ZonalStatisticsAsTable(ras_record, "LineOID", ras_name, zstat_result, "DATA", "MEAN")
                arcpy.AddJoin_management("tmpFC", "LineOID", zstat_result, "LineOID", "KEEP_ALL")
                arcpy.CalculateField_management("tmpFC", field_name, "!zstat_result.MEAN!", "PYTHON_9.3")
                arcpy.RemoveJoin_management("tmpFC")
                arcpy.Delete_management(zstat_result)
                arcpy.AddMessage("Parameter " + field_name + " is summarized...")
            arcpy.AddMessage("Polygon with LineOID " + str(row[0]) + " is complete...")
    arcpy.SelectLayerByAttribute_management("tmpFC", "CLEAR_SELECTION")
    gc.disable()
    return "tmpFC"

def main(inFC, inParam):
    addFieldsFC = addParamFields(inFC, inParam)
    calcParamsFC = calcParams(addFieldsFC, inParam)
    arcpy.TableToTable_conversion(calcParamsFC, outDir, "ws_cond_param.dbf")
    arcpy.Delete_management(addFieldsFC)
    arcpy.Delete_management(calcParamsFC)

main(calc_ply, param_list)

# end processing time
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("-------------------------------------")
arcpy.AddMessage("Processing completed at " + str(printTime))
curTime = time.time()
totalTime = (curTime - startTime)/60.0
arcpy.AddMessage("Total processing time was " + str(round(totalTime,2)) + " minutes.")