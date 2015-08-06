# file name:	polystat_cond.py
# description:	This tool is a derivation of the PolyStat tool, but it has been refactored to work specifically work 
#				for the Conductivity model.  The tool calculates the mean value of 19 environmental parameters ( 
#	            raster datasets) per polygon (in this case, upstream catchment areas), and adds that value to a field 
#				in the polygon's attribute table.  The resulting attribute table can then serve as an input to the
#				Olson et al Random Forest conductivity model.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.1

import os, sys, time, gc, arcpy
from arcpy.sa import *
from time import strftime
# enable garbage collection
gc.enable()

# start processing time
startTime = time.time()
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("Processing started at " + str(printTime))
arcpy.AddMessage("------------------------------------")

# create scratch workspace and ArcPy environment settings
temp_dir = arcpy.GetSystemEnvironment("TEMP")
scratch_gdb = arcpy.CreateFileGDB_management(temp_dir, "scratch.gdb", "CURRENT")
arcpy.env.workspace = temp_dir + r"\scratch.gdb"
arcpy.env.overwriteOutput = True

# Check out Spatial Analyst
arcpy.CheckOutExtension("Spatial")

# input variables:
calc_ply = arcpy.GetParameterAsText(0) # polygon feature class (i.e. catchments)
##### calc_ply = r"C:\repo\conductivity\MFJD_huc6_catch.shp"
envDir = arcpy.GetParameterAsText(1) # directory containing the conductivity model raster inputs
##### envDir = r"C:\JL\ISEMP\Data\ec\model\Grids"
outDir = arcpy.GetParameterAsText(2) # directory location for the final polygon feature class
##### outDir = r"C:\repo\conductivity"
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
	arcpy.AddMessage("Calculating statistics for model input parameters, per polygon...")
	arcpy.MakeFeatureLayer_management(in_poly, "in_ply_lyr")
	# create blank table with fields for model parameters
	param_table = arcpy.CreateTable_management(scratch_gdb, "param_table")
	arcpy.AddField_management(param_table, "LineOID", "SHORT")
	for p in param_list:
 		arcpy.AddField_management(param_table, p[0] + "_MN", "DOUBLE")
 	# main processing loop
	with arcpy.da.SearchCursor(in_poly, ["LineOID"]) as cursor:
		for row in cursor:
			expr = """ "LineOID" = """ + str(row[0])
			arcpy.SelectLayerByAttribute_management("in_ply_lyr", "NEW_SELECTION", expr)
			ras_record = arcpy.PolygonToRaster_conversion("in_ply_lyr", "LineOID", "ras_record", "CELL_CENTER", "#", 30)
			arcpy.AddField_management(ras_record, "LineOID", "LONG")
			arcpy.CalculateField_management(ras_record, "LineOID", "!Value!", "PYTHON_9.3")
			for r in in_param:
				field_name = r[0]
				ras_name = envDir + "\\" + r[1]
				arcpy.AddField_management(ras_record, field_name, "DOUBLE")
				ZonalStatisticsAsTable(ras_record, "LineOID", ras_name, "temp_stat_record", "DATA", "MEAN")
				arcpy.MakeRasterLayer_management(ras_record, "ras_record_lyr")
				arcpy.MakeTableView_management("temp_stat_record", "temp_stat_view")
				arcpy.AddJoin_management("ras_record_lyr", "LineOID", "temp_stat_view", "LineOID", "KEEP_ALL")
				arcpy.CalculateField_management("ras_record_lyr", "VAT_ras_record." + field_name, "!temp_stat_record.MEAN!", "PYTHON_9.3")
				arcpy.RemoveJoin_management("ras_record_lyr")
				arcpy.MakeTableView_management("ras_record_lyr", "ras_view")
				arcpy.Delete_management("temp_stat_record")
			arcpy.Append_management("ras_view", param_table, "NO_TEST")
			arcpy.AddMessage("Polygon with LineOID: " + str(row[0]) + " is complete...")
	##### result = arcpy.FeatureClassToFeatureClass("temp_ply_view", outDir, "ws_params.shp")
	return param_table

out_table = main(calc_ply, param_list)
arcpy.TableToTable_conversion(out_table, outDir, "ws_cond_param.dbf")
arcpy.Delete_management(scratch_gdb)

# end processing time
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("-------------------------------------")
arcpy.AddMessage("Processing completed at " + str(printTime))
curTime = time.time()
totalTime = (curTime - startTime)/60.0
arcpy.AddMessage("Total processing time was " + str(totalTime) + " minutes.")