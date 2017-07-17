# file name:	polystat_cond.py
# description:	This tool is a derivation of the PolyStat tool, but it has been refactored to work specifically  
#				for the Conductivity model.  The tool calculates the mean value of 19 environmental parameters  
#	            (raster datasets) per polygon (in this case, upstream catchment areas), and adds that value to a  
#				field in the polygon's attribute table.  The resulting attribute table can then serve as an input 
#				to the Olson et. al. Random Forest conductivity model (via the predict_cond.py script).
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.5.5

import gc, sys, arcpy
import os
import time
from arcpy.sa import *
from time import strftime
import metadata.meta_sfr as meta_sfr
import metadata.meta_rs as meta_rs
import riverscapes as rs

version = "0.5.6"

# start processing time
startTime = time.time()
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("Processing started at " + str(printTime))
arcpy.AddMessage("------------------------------------")

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# input variables:
calc_ply = arcpy.GetParameterAsText(0) # polygon feature class (i.e. catchments)
env_dir = arcpy.GetParameterAsText(1) # directory containing the conductivity model raster inputs.
out_tbl = arcpy.GetParameterAsText(2) # directory location for parameter summary table output.
rs_bool = arcpy.GetParameterAsText(3) # boolean parameter to indicate if Riverscapes project outputs are required
wshd_name = arcpy.GetParameterAsText(4) # name of project watershed. required for Riverscape XML file.
rs_proj_name = arcpy.GetParameterAsText(5) # Riverscapes project name
rs_real_name = arcpy.GetParameterAsText(6) # Riverscapes realization name
rs_dir = arcpy.GetParameterAsText(7) # directory where Riverscapes project files will be written


# constants
PARAM_LIST= [["AtmCa", "ca_avg_250"], # list of model parameter names and associated raster dataset names
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


def checkLineOID(in_fc):
    """Checks the input upstream catchment area polygon feature class for the
    presence of an attribute field named 'LineOID'.

    Args:
        in_fc: Input upstream catchment area polygon feature class

    Returns:
        A boolean true or false value.
    """
    fieldName = "LineOID"
    fields = arcpy.ListFields(in_fc, fieldName)
    for field in fields:
        if field.name == fieldName:
            return True
        else:
            return False


def addParamFields(in_fc, inParam):
    """Removes unnecessary fields and adding blank model parameter fields
    to the input upstream catchment area polygon feature class.

    Args:
        in_fc: Input upstream catchment area polygon feature class
        inParam: 2D list of model parameter names and associated raster
        dataset names

    Returns:
        tmp_fc: Polyline feature class with added parameter fields
    """
    arcpy.AddMessage("Preparing parameter fields in " + in_fc + "...")
    tmpFC = arcpy.FeatureClassToFeatureClass_conversion(in_fc, "in_memory", "tmp_fc")
    field_obj_list = arcpy.ListFields(tmpFC)
    field_name_list = []
    if checkLineOID(in_fc) == True:
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


def calcParams(in_fc, env_dir, inParam):
    """Build attribute table os summarized parameter values for the input
    feature class.

    Args:
        in_fc: Input upstream catchment area polygon feature class
        inParam: 2D list of model parameter names and associated raster
        dataset names

    Returns:
        An in-memory polygon feature class, with summarized parameter values
        for each upstream catchment area polygon record.

    """
    arcpy.AddMessage("Summarizing parameter values per catchment area polygon...")
    gc.enable()
    with arcpy.da.SearchCursor(in_fc, ["LineOID"]) as cursor:
        for row in cursor:
            expr = """ "LineOID" = """ + str(row[0])
            arcpy.MakeFeatureLayer_management(in_fc, "tmpFC")
            arcpy.SelectLayerByAttribute_management("tmpFC", "NEW_SELECTION", expr)
            ras_record = arcpy.PolygonToRaster_conversion("tmpFC", "LineOID", "in_memory\\ras_record",
                                                          "CELL_CENTER", "#", 30)
            arcpy.AddField_management(ras_record, "LineOID", "LONG")
            arcpy.CalculateField_management(ras_record, "LineOID", "!Value!", "PYTHON_9.3")
            arcpy.CalculateStatistics_management(ras_record)
            for r in inParam:
                field_name = r[0]
                ras_name = env_dir + "\\" + r[1]
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


def clear_inmemory():
    """Clears all in_memory datasets."""
    arcpy.env.workspace = r"IN_MEMORY"
    arcpy.AddMessage("Deleting in_memory data...")

    list_fc = arcpy.ListFeatureClasses()
    list_tbl = arcpy.ListTables()

    # for each FeatClass in the list of fcs's, delete it.
    for f in list_fc:
        arcpy.Delete_management(f)
    # for each TableClass in the list of tab's, delete it.
    for t in list_tbl:
        arcpy.Delete_management(t)
    return


def metadata(ecXML, calc_ply, env_dir, out_tbl, rs_bool, wshd_name, real_name, real_id):
    """Builds and writes an XML file according to the Riverscapes Project specifications

        Args:
            ecXML: Project XML object instance
    """

    # Finalize metadata
    timeStart, timeStop = ecXML.finalize()

    ecXML.getOperator()
    # Add Meta tags
    huc_id = rs.getHUCID(wshd_name)
    ecXML.addMeta("HUCID", huc_id, ecXML.project)
    ecXML.addMeta("Region", "CRB", ecXML.project)
    ecXML.addMeta("Watershed", wshd_name, ecXML.project)
    # Add Realization tags
    ecXML.addRealization(real_name, real_id, timeStop, version, ecXML.getUUID())
    ecXML.addMeta("Operator", ecXML.operator, ecXML.project, "EC", real_id)
    ecXML.addMeta("ComputerID", ecXML.computerID, ecXML.project, "EC", real_id)
    ecXML.addMeta("Polystat Start Time", timeStart, ecXML.project, "EC", real_id)
    ecXML.addMeta("Polystat Stop Time", timeStop, ecXML.project, "EC", real_id)
    # Add Parameter tags
    ecXML.addParameter("Environmental Parameter Workspace", env_dir, ecXML.project, "EC", real_id)
    # Add Realization input tags
    ecXML.addRealizationInputData(ecXML.project, "Vector", "EC", real_id, "Catchment Area Polygons", calc_ply, "CATCH_POLY", ecXML.getUUID())
    ecXML.addRealizationInputRef(ecXML.project, "Raster", "EC", real_id, "PARAMs")
    # Add Analysis output tags
    ecXML.addOutput("DataTable", "Environmental Parameter Table", out_tbl, ecXML.realizations, "EC", real_id, "PARAM_TABLE",
                    ecXML.getUUID())
    ecXML.write()


def main(in_fc, out_tbl, env_dir, inParam, rs_bool, wshd_name='', proj_name = '', real_name='', rs_dir=''):
    """Main processing function"""

    in_fc_dir = os.path.dirname(in_fc)
    in_fc_name = os.path.basename(in_fc)
    out_dir = os.path.dirname(out_tbl)
    out_tbl_name = os.path.basename(out_tbl)

    in_fc_type = arcpy.Describe(in_fc_dir).workspaceType
    if in_fc_type == "LocalDatabase":
        in_shp_name = in_fc_name + ".shp"

    # initiate generic metadata XML object
    time_stamp = time.strftime("%Y%m%d%H%M")
    out_xml = os.path.join(out_dir, "{0}_{1}.{2}".format("meta_preprocess", time_stamp, "xml"))
    mWriter = meta_sfr.MetadataWriter("Pre-process Environmental Parameters", "0.4")
    mWriter.createRun()
    mWriter.currentRun.addParameter("Catchment area feature class", in_fc)
    mWriter.currentRun.addParameter("Output environmental parameter table", out_tbl)
    mWriter.currentRun.addParameter("Environmental parameter workspace", env_dir)
    mWriter.currentRun.addParameter("Output metadata XML", out_xml)

    # initiate Riverscapes project XML object
    if rs_bool == "true":
        rs.writeRSRoot(rs_dir)
        rs_xml = "{0}\\{1}".format(rs_dir, "project.rs.xml")
        projectXML = meta_rs.ProjectXML("polystat", rs_xml, "EC", proj_name)

    # run the environmental parameter summary
    addFieldsFC = addParamFields(in_fc, inParam)
    calcParamsFC = calcParams(addFieldsFC, env_dir, inParam)
    arcpy.TableToTable_conversion(calcParamsFC, out_dir, out_tbl_name)

    # finalize and write generic XML file
    tool_status = "Success"
    mWriter.finalizeRun(tool_status)
    mWriter.writeMetadataFile(out_xml)

    # Riverscapes output, including project XML and data files
    if rs_bool == "true":
        arcpy.AddMessage("Exporting as a Riverscapes project...")
        real_id = rs.getRealID(time_stamp)
        # copy input/output data to Riverscapes project directories
        abs_fc_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 0, real_id), in_fc_name)
        abs_tbl_path = os.path.join(rs.getRSDirAbs(rs_dir, 1, 1, real_id), out_tbl_name)
        rs.writeRSDirs(rs_dir, real_id)
        rs.copyRSFiles(in_fc, abs_fc_path)
        rs.copyRSFiles(out_tbl, abs_tbl_path)
        # write project XML file. Note the use of the 'relative path version' of get directories function
        rel_fc_path = os.path.join(rs.getRSDirRel(1, 0, real_id), in_shp_name)
        rel_tbl_path = os.path.join(rs.getRSDirRel(1, 1, real_id), out_tbl_name)
        metadata(projectXML,
                 rel_fc_path,
                 env_dir,
                 rel_tbl_path,
                 rs_bool,
                 wshd_name,
                 real_name,
                 real_id)

    # clean up
    arcpy.Delete_management(addFieldsFC)
    arcpy.Delete_management(calcParamsFC)
    clear_inmemory()

if __name__ == "__main__":
    main(calc_ply, out_tbl, env_dir, PARAM_LIST, rs_bool, wshd_name, rs_proj_name, rs_real_name, rs_dir)


# end processing time
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("-------------------------------------")
arcpy.AddMessage("Processing completed at " + str(printTime))
curTime = time.time()
totalTime = (curTime - startTime)/60.0
arcpy.AddMessage("Total processing time was " + str(round(totalTime,2)) + " minutes.")