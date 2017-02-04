import os
import shutil
import arcpy
from random import choice
from string import digits
from string import ascii_uppercase

# constants
RS_SUBDIRS = ["Inputs", "Realizations"] # directories in the Riverscape Project root
RS_OUTDIRS = ["Polystat", "Predict"] # directories storing Riverscape realization outputs

HUCID_DICT = {"Asotin":"17060103",
              "Big-Navarro-Garcia (CA)":"18010108",
              "Entiat":"17020010",
              "John Day":"17070204",
              "Lemhi":"17060204",
              "Lolo Creek":"1706030602",
              "Methow":"17020008",
              "Minam":"1706010505",
              "Region 17":"17",
              "South Fork Salmon":"17060208",
              "Tucannon":"17060107",
              "Umatilla":"17070103",
              "Upper Grande Ronde":"17060104",
              "Walla Walla":"17070102",
              "Wenatchee":"17020011",
              "Yankee Fork":"1706020105"}


def writeRSRoot(rs_root):
    if os.path.exists(rs_root):
        shutil.rmtree(rs_root)
        os.mkdir(rs_root)
        os.chmod(rs_root, 0o777)
    else:
        os.mkdir(rs_root)
        os.chmod(rs_root, 0o777)


def writeRSDirs(rs_root, real_id):
    """Writes optional Riverscape project file folders"""
    for subdir in RS_SUBDIRS:
        os.makedirs(os.path.join(rs_root, subdir))
    for outdir in RS_OUTDIRS:
        os.makedirs(os.path.join(rs_root, real_id, RS_SUBDIRS[1], outdir))


def copyRSFiles(from_file, out_file):
    from_desc = arcpy.Describe(from_file)
    if from_desc.dataType == "DbaseTable":
        arcpy.MakeTableView_management(from_file, "from_file_view")
        arcpy.CopyRows_management("from_file_view", out_file)
    elif from_desc.dataType == "FeatureClass" or from_desc.dataType == "ShapeFile":
        arcpy.MakeFeatureLayer_management(from_file, "from_file_lyr")
        arcpy.CopyFeatures_management("from_file_lyr", out_file)


def getRSdirs(root, subdir_index='', outdir_index='', real_id=''):
    if subdir_index != '' and outdir_index != '':
        return os.path.join(root, RS_SUBDIRS[subdir_index], real_id, RS_OUTDIRS[outdir_index]) # Realizations
    if subdir_index != '' and outdir_index == '':
        return os.path.join(root, RS_SUBDIRS[subdir_index]) # Inputs


def getHUCID(wshd_name):
    huc_id = HUCID_DICT[wshd_name]
    return huc_id

def getRealID():
    return "real" + ''.join(choice(ascii_uppercase + digits) for i in range(8))