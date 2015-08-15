# file name:	polystat_cond.py
# description:	This tool is a derivation of the PolyStat tool, but it has been refactored to work specifically  
#				for the Conductivity model.  The tool calculates the mean value of 19 environmental parameters  
#	            (raster datasets) per polygon (in this case, upstream catchment areas), and adds that value to a  
#				field in the polygon's attribute table.  The resulting attribute table can then serve as an input 
#				to the Olson et al Random Forest conductivity model.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.2

import os, sys, time, gc, arcpy
from arcpy.sa import *
from time import strftime
gc.enable()

# start processing time
startTime = time.time()
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("Processing started at " + str(printTime))
arcpy.AddMessage("------------------------------------")

arcpy.env.overwriteOutput = True

# Check out Spatial Analyst
arcpy.CheckOutExtension("Spatial")

# input variables:
calc_ply = arcpy.GetParameterAsText(0) # polygon feature class (i.e. catchments)
outDir = arcpy.GetParameterAsText(1) # directory location for the final polygon feature class
envDir = arcpy.GetParameterAsText(2) # directory containing the conductivity model raster inputs

param_list = [["AtmCa", "ca_avg_250"], # list of raster dataset names and associated field names
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

# main function that performs the parameter summary
def main(in_poly, in_param):
	# prepare the input polygon feature class by stripping all unnecessary fields and adding in blank model parameter fields
	arcpy.AddMessage("Calculating statistics for model input parameters, per polygon...")
	tmp_ply = arcpy.FeatureClassToFeatureClass_conversion(in_poly, "in_memory", "tmp_ply")
	field_obj_list = arcpy.ListFields(tmp_ply)
	field_name_list = []
	for f in field_obj_list:
		if not f.type == "Geometry" and not f.type == "OID" and not f.name == "LineOID":
			field_name_list.append(str(f.name))
	arcpy.DeleteField_management(tmp_ply, field_name_list)
	for p in in_param:
 		arcpy.AddField_management(tmp_ply, p[0], "DOUBLE")

 	# main processing loop
	with arcpy.da.SearchCursor(tmp_ply, ["LineOID"]) as cursor:
		for row in cursor:
			expr = """ "LineOID" = """ + str(row[0])
			arcpy.MakeFeatureLayer_management(tmp_ply, "tmp_ply_view")
			arcpy.SelectLayerByAttribute_management("tmp_ply_view", "NEW_SELECTION", expr)
			ras_record = arcpy.PolygonToRaster_conversion("tmp_ply_view", "LineOID", "in_memory\\ras_record", "CELL_CENTER", "#", 30)
			arcpy.AddField_management(ras_record, "LineOID", "LONG")
			arcpy.CalculateField_management(ras_record, "LineOID", "!Value!", "PYTHON_9.3")
			arcpy.CalculateStatistics_management(ras_record)
			for r in in_param:
				field_name = r[0]
				ras_name = envDir + "\\" + r[1]
				zstat_result = "in_memory\\zstat_result"
				ZonalStatisticsAsTable(ras_record, "LineOID", ras_name, zstat_result, "DATA", "MEAN")
				arcpy.AddJoin_management("tmp_ply_view", "LineOID", zstat_result, "LineOID", "KEEP_ALL")
				arcpy.CalculateField_management("tmp_ply_view", field_name, "!zstat_result.MEAN!", "PYTHON_9.3")
				arcpy.RemoveJoin_management("tmp_ply_view")
				arcpy.Delete_management(zstat_result)
			arcpy.AddMessage("Polygon with LineOID " + str(row[0]) + " is complete...")
	arcpy.SelectLayerByAttribute_management("tmp_ply_view", "CLEAR_SELECTION")
	return "tmp_ply_view"

result = main(calc_ply, param_list)
arcpy.FeatureClassToFeatureClass_conversion(result, outDir, "ws_cond_param.shp")
arcpy.Delete_management(result)

# end processing time
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("-------------------------------------")
arcpy.AddMessage("Processing completed at " + str(printTime))
curTime = time.time()
totalTime = (curTime - startTime)/60.0
arcpy.AddMessage("Total processing time was " + str(totalTime) + " minutes.")