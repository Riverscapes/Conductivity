import os
import arcpy
import metadata.meta_rs as meta
import create_project
import polystat_cond
import predict_cond

# CONSTANTS
version = "1.0.3"
list_wshd = ['Big-Navarro-Garcia (CA)',
             'Clearwater',
             'Entiat',
             'Hells Canyon',
             'Imnaha',
             'Klickitat',
             'Lemhi',
             'Little Salmon',
             'Lochsa',
             'Lolo Creek',
             'Lower John Day',
             'Lower North Fork Clearwater',
             'Lower Salmon',
             "Lower Selway",
             'Lower Snake-Asotin',
             'Lower Snake-Tucannon',
             'Lower Yakima',
             'Methow',
             'Middle Fork Clearwater',
             'Middle Fork John Day',
             'Middle Salmon-Panther',
             'Minam',
             'North Fork John Day',
             'Okanogan',
             'Pahsimeroi',
             'South Fork Clearwater',
             'South Fork Salmon',
             'Umatilla',
             'Upper Grande Ronde',
             'Upper John Day',
             'Upper Middle Fork Salmon',
             'Upper North Fork Clearwater',
             'Upper Selway',
             'Upper Yakima',
             'Walla Walla',
             'Wallowa',
             'Wenatchee']


class Toolbox(object):
    def __init__(self):
        self.label = 'Conductivity Tools'
        self.alias = 'Conductivity'
        self.tools = [CreateProjectTool, PolystatCondTool, PredictCondTool]
        self.description = "Modeling electrical conductivity for a spatially-explicit stream network."


class CreateProjectTool(object):
    def __init__(self):
        self.label = 'Create Riverscapes Project'
        self.description = "This tool creates a new Riverscapes project XML " \
                           "file and associated data directories, based on the " \
                           "Riverscapes protocol."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        reload(create_project)

        param0 = arcpy.Parameter(
            name='rs_dir',
            displayName='Riverscapes workspace',
            parameterType='Required',
            direction='Input',
            datatype='DEWorkspace')
        param0.filter.list = ['File System']

        param1 = arcpy.Parameter(
            name='region_name',
            displayName='Region name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')
        param1.filter.list = ['CRB']

        param2 = arcpy.Parameter(
            name='wshd_name',
            displayName='Watershed name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')
        param2.filter.list = list_wshd

        param3 = arcpy.Parameter(
            name='proj_name',
            displayName='Riverscapes project name',
            parameterType='Required',
            direction='Input',
            datatype='GPString')

        return [param0,
                param1,
                param2,
                param3]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        reload(create_project)
        create_project.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText)
        return


class PolystatCondTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Pre-process Environmental Parameters'
        self.description = "The Pre-process Environmental Parameters tool" \
                           " takes a user-supplied polygon feature class " \
                           "(i.e. basin or catchment areas), and calculates " \
                           "the mean value for each of 19 environmental " \
                           "parameters (represented as raster datasets) " \
                           "intersecting each polygon feature, using Zonal " \
                           "Statistics. The output is a table, with a record " \
                           "for each polygon feature, and an attribute field " \
                           "with stores the mean value for each parameter. " \
                           "This tool is the first of a two-step process to " \
                           "predict electrical conductivity for a geospatial " \
                           "stream network."

        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        reload(polystat_cond)

        param0 = arcpy.Parameter(
            name = 'calc_ply',
            displayName = 'Catchment area feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'GPFeatureLayer')
        param0.filter.list = ['Polygon']

        param1 = arcpy.Parameter(
            name = 'env_dir',
            displayName = 'Environmental parameter workspace',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DEWorkspace')
        param1.filter.list = ['File System','Local Database']

        param2 = arcpy.Parameter(
            name = 'out_tbl',
            displayName = 'Output environmental parameter table',
            parameterType = 'Required',
            direction = 'Output',
            datatype = 'DETable')

        param3 = arcpy.Parameter(
            name = 'rs_bool',
            displayName = 'Is this a Riverscapes project?',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPBoolean',
            category='Riverscapes Project Management')

        param4 = arcpy.Parameter(
            name = 'rs_dir',
            displayName = 'Riverscapes workspace',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'DEWorkspace',
            category = 'Riverscapes Project Management')
        param4.filter.list = ['File System']

        param5 = arcpy.Parameter(
            name = 'rs_proj_name',
            displayName = 'Riverscapes project name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            enabled = 'false',
            category = 'Riverscapes Project Management')

        param6 = arcpy.Parameter(
            name = 'rs_real_name',
            displayName = 'Realization name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            category = 'Riverscapes Project Management')


        return [param0,
                param1,
                param2,
                param3,
                param4,
                param5,
                param6]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        if parameters[3].value == True:
            parameters[4].enabled = True
            parameters[6].enabled = True
            # add project name from XML if it exists
            if parameters[4].altered == True:
                if os.path.isdir(str(parameters[4].value)):
                    rs_xml = "{0}\\{1}".format(parameters[4].value, "project.rs.xml")
                    if os.path.isfile(str(rs_xml)):
                        projectXML = meta.ProjectXML("existing", rs_xml, "EC")
                        proj_name = projectXML.getProjectName(projectXML.project, "Name")
                        parameters[5].value = proj_name[0]
        else:
            parameters[4].enabled = False
            # the Project Name parameter is always disabled for editing in this tool
            parameters[5].value = ''
            parameters[6].enabled = False

    def updateMessages(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[4].altered == True:
            pathProjectInputs = "{0}\\{1}".format(parameters[4].value,"ProjectInputs")
            pathRealizations = "{0}\\{1}".format(parameters[4].value, "Realizations")
            # check if this is a Riverscapes project folder
            if os.path.exists(pathProjectInputs) and os.path.exists(pathRealizations):
                rs_xml = "{0}\\{1}".format(parameters[4].value, "project.rs.xml")
                if not os.path.isfile(rs_xml):
                    parameters[4].setErrorMessage("This is not a valid Riverscapes project!")
            else:
                parameters[4].setErrorMessage("Valid Riverscape data folders are missing from this directory!")
        return

    def execute(self, p, messages):
        polystat_cond.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText,
                         p[4].valueAsText,
                         p[5].valueAsText,
                         p[6].valueAsText)

        # # # DEBUG
        # calc_ply = r"C:\JL\Testing\conductivity\Issue13\TestCase\source\catch_test.shp"
        # env_dir = r"C:\JL\ISEMP\Data\ec\model\Grids_rsmp"
        # out_tbl = r"C:\JL\Testing\conductivity\Issue13\TestCase\outputs\cond_params.dbf"
        # rs_bool = "true"
        # rs_proj_name = "Lower Selway Project"
        # rs_real_name = "Test Realization 01"
        # rs_dir = r"C:\JL\Testing\conductivity\Issue13\TestCase\rsp"
        #
        # polystat_cond.main(calc_ply, env_dir, out_tbl, rs_bool, rs_dir, rs_proj_name, rs_real_name)

        return


class PredictCondTool(object):
    def __init__(self):
        self.label = 'Predict Electrical Conductivity for a Stream Network'
        self.description = "This tool uses the output from the Pre-process " \
                           "Environmental Parameters tool to generate precited " \
                           "conductivity values for each segment in a stream " \
                           "network, using a pre-existing Random Forest model. " \
                           "More information about the Random Forest conductivity " \
                           "model can be found in Olson and Hawkins, 2012."

        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        reload(predict_cond)

        param0 = arcpy.Parameter(
            name = 'in_fc',
            displayName = 'Stream network polyline feature class',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DEFeatureClass')
        param0.filter.list = ['Polyline']

        param1 = arcpy.Parameter(
            name = 'in_params',
            displayName = 'Environmental parameter table',
            parameterType = 'Required',
            direction = 'Input',
            datatype = 'DETable')

        param2 = arcpy.Parameter(
            name = 'out_fc',
            displayName = 'Output polyline feature with conductivity values',
            parameterType = 'Required',
            direction = 'Output',
            datatype = 'DEFeatureClass')
        param2.filter.list = ['Polyline']

        param3 = arcpy.Parameter(
            name = 'rs_bool',
            displayName = 'Is this a Riverscapes project?',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPBoolean',
            category='Riverscapes Project Management')

        param4 = arcpy.Parameter(
            name = 'rs_dir',
            displayName = 'Riverscapes workspace',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'DEWorkspace',
            category='Riverscapes Project Management')
        param4.filter.list = ['File System']

        param5 = arcpy.Parameter(
            name = 'rs_proj_name',
            displayName = 'Project name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            enabled = 'false',
            category = 'Riverscapes Project Management')

        param6 = arcpy.Parameter(
            name = 'rs_real_name',
            displayName = 'Realization name',
            parameterType = 'Optional',
            direction = 'Input',
            datatype = 'GPString',
            category='Riverscapes Project Management')
        param6.filter.type = "ValueList"
        param6.filter.list = []

        return [param0,
                param1,
                param2,
                param3,
                param4,
                param5,
                param6]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""

        if parameters[3].value == True:
            parameters[4].enabled = True
            parameters[6].enabled = True
            # add project name from XML if it exists
            if parameters[4].altered == True:
                if os.path.isdir(str(parameters[4].value)):
                    rs_xml = "{0}\\{1}".format(parameters[4].value, "project.rs.xml")
                    if os.path.isfile(str(rs_xml)):
                        projectXML = meta.ProjectXML("existing", rs_xml, "EC")
                        proj_name = projectXML.getProjectName(projectXML.project, "Name")
                        parameters[5].value = proj_name[0]
                        real_names = projectXML.getRealNames(projectXML.project, "EC")
                        parameters[6].filter.list = real_names
        else:
            parameters[4].enabled = False
            # the Project Name parameter is always disabled for editing in this tool
            parameters[5].value = ''
            parameters[6].enabled = False

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[6].altered == True:
            pathProjectInputs = "{0}\\{1}".format(parameters[4].value,"ProjectInputs")
            pathRealizations = "{0}\\{1}".format(parameters[4].value, "Realizations")
            # check if this is a Riverscapes project folder
            if os.path.exists(pathProjectInputs) and os.path.exists(pathRealizations):
                rs_xml = "{0}\\{1}".format(parameters[4].value, "project.rs.xml")
                if not os.path.isfile(rs_xml):
                    parameters[6].setErrorMessage("This is not a valid Riverscapes project!")
            else:
                parameters[6].setErrorMessage("Valid Riverscape data folders are missing from this directory!")
        return

    def execute(self, p, messages):
        predict_cond.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText,
                         p[4].valueAsText,
                         p[5].valueAsText,
                         p[6].valueAsText)
        return

# DEBUG
# def main():
#     tbx = Toolbox()
#     tool = PolystatCondTool()
#     tool.execute(tool.getParameterInfo(),None)
#
# if __name__ == '__main__':
#     main()