# file name:	create_project.py
# description:	The Create Riverscapes Project tool creates a Riverscapes project XML file and the
#               associated input and output data folders. The tool only creates new Riverscape
#               projects, and can't be used to alter existing Riverscapes project. Running this tool
#               is optional, but it should be run before solar modeling if this is a Riverscapes
#               project.
# dependencies: arcpy

import arcpy
import os.path
import metadata.meta_rs as meta_rs
import riverscapes as rs


def metadata(ecXML,
             region_name,
             wshd_name,
             project_name):
    """Builds and writes an XML file according to the Riverscapes Project specifications

        Args:
            solarXML: Project XML object instance
    """

    ecXML.getOperator()
    # Add Project Meta tags
    huc_id = rs.getHUCID(wshd_name)
    ecXML.addMeta("HUCID", huc_id, ecXML.project)
    ecXML.addMeta("Region", region_name, ecXML.project)
    ecXML.addMeta("Watershed", wshd_name, ecXML.project)

    ecXML.write()


def main(rs_dir, region_name, wshd_name, proj_name):
    rs_xml = "{0}\\{1}".format(rs_dir, "project.rs.xml")
    # initiate Riverscapes project XML object and create folders, if user-supplied workspace is blank
    if not os.path.isfile(os.path.join(rs_dir, rs_xml)):
        rs.writeRSRoot(rs_dir)
        projectXML = meta_rs.ProjectXML("new", rs_xml, "EC", proj_name)
        metadata(projectXML, region_name, wshd_name, proj_name)
    else:
        arcpy.AddError("Riverscapes project file already exists! Please choose an empty directory...")

    return