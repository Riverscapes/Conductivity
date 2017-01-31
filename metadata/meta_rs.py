import xml, os
import uuid
import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from getpass import getuser
from socket import gethostname


class ProjectXML:
    """Creates an instance of a project xml.

    Args:
        filepath: XML file name. Can be an existing or new file.
        projType: Riverscape project type.  Should not be included if instance is created from existing XML file.
        name: Riverscape project name. Should not be included if instance is created from existing XML file.

    Returns:
        ProjectXML object instance
    """

    def __init__(self, tool, filepath, projType='', name=''):
        # Get the start timestamp
        self.timestampStart = datetime.datetime.now()

        self.logFilePath = filepath
        if tool == "polystat":
            if os.path.isfile(self.logFilePath):
                os.remove(self.logFilePath)

            self.projectTree = ET.ElementTree(ET.Element("Project"))
            self.project = self.projectTree.getroot()

            # Set up a root Project node
            self.project.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            self.project.set('xsi:noNamespaceSchemaLocation',
                             'https://raw.githubusercontent.com/Riverscapes/Program/master/Project/XSD/V1/Project.xsd')

            # Set up the <Name> and <ProjectType> tags
            self.name = ET.SubElement(self.project, "Name")
            self.name.text = name
            self.projectType = ET.SubElement(self.project, "ProjectType")
            self.projectType.text = projType

            # Add some containers we will fill out later
            self.Inputs = ET.SubElement(self.project, "Inputs")
            self.realizations = ET.SubElement(self.project, "Realizations")

        else:
            if os.path.isfile(self.logFilePath):
                self.projectTree = ET.parse(filepath)
                self.project = self.projectTree.getroot()

        self.ECrealizations = []

    def getOperator(self):
        """gets operator name and computer ID"""
        self.operator = getuser()
        self.computerID = gethostname()

    def addMeta(self, name, value, parentNode):
        """adds metadata tags to the project xml document"""
        metaNode = parentNode.find("MetaData")
        if metaNode is None:
            metaNode = ET.SubElement(parentNode, "MetaData")

        node = ET.SubElement(metaNode, "Meta")
        node.set("name", name)
        node.text = str(value)

    def addProjectInput(self, itype, name, path, parentNode, iid='', guid='', append=''):
        """Adds a project input tag"""
        if append == "True":
            inputNode = parentNode.find("Inputs")
            typeNode = ET.SubElement(inputNode, itype)
        else:
            typeNode = ET.SubElement(self.Inputs, itype)
        if iid is not '':
            typeNode.set('id', iid)
        if guid is not '':
            typeNode.set('guid', guid)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

    def addRealization(self, name, dateCreated='', guid='', productVersion=''):
        """adds an EC realization tag to the project xml document"""
        node = ET.SubElement(self.realizations, "EC")
        if dateCreated is not '':
            node.set('dateCreated', dateCreated)
        if guid is not '':
            node.set('guid', guid)
        if productVersion is not '':
            node.set('productVersion', productVersion)
        nameNode = ET.SubElement(node, "Name")
        nameNode.text = str(name)
        self.ECrealizations.append(node)

    def addParameter(self, name, value, parentNode):
        """adds parameter tags to the project xml document"""
        paramNode = parentNode.find("Parameters")
        if paramNode is None:
            paramNode = ET.SubElement(parentNode, "Parameters")

        node = ET.SubElement(paramNode, "Param")
        node.set("name", name)
        node.text = str(value)

    def addECInput(self, parentNode, type, ref='', append=''):
        """adds realization input tags"""
        if parentNode == self.project:
            realizationNode = parentNode.find("Realizations")
            inputsNode = realizationNode.find("Inputs")
        elif parentNode == self.realizations:
            inputsNode = parentNode.find("Inputs")
            if inputsNode is None:
                inputsNode = ET.SubElement(parentNode, "Inputs")
        if append == 'True' and type == 'Vector':
            vectorNode = ET.SubElement(inputsNode, "Vector")
            if ref is not '':
                vectorNode.set('ref', ref)
        elif append != 'True' and type == 'Vector':
            vectorNode = inputsNode.find("Vector")
            if vectorNode is None:
                vectorNode = ET.SubElement(inputsNode, "Vector")
            if ref is not '':
                vectorNode.set('ref', ref)
        if append == 'True' and type == 'DataTable':
            tableNode = ET.SubElement(inputsNode, "DataTable")
            if ref is not '':
                tableNode.Set('ref', ref)
        elif append != 'True' and type == 'DataTable':
            tableNode = inputsNode.find("DataTable")
            if tableNode is None:
                tableNode = ET.SubElement(inputsNode, "Vector")
            if ref is not '':
                tableNode.set('ref', ref)

    def addOutput(self, otype, name, path, parentNode, oid='', guid=''):
        """adds an output tag to an analysis tag in the project xml document"""
        if parentNode == self.project:
            realizationNode = parentNode.find("Realizations")
            analysisNode = realizationNode.find("Analysis")
            outputsNode = ET.SubElement(analysisNode, "Outputs")
        elif parentNode == self.realizations:
            analysisNode = parentNode.find("Analysis")
            if analysisNode is None:
                analysisNode = ET.SubElement(parentNode, "Analysis")
                outputsNode = analysisNode.find("Outputs")
                if outputsNode is None:
                    outputsNode = ET.SubElement(analysisNode, "Outputs")
        typeNode = ET.SubElement(outputsNode, otype)
        if oid is not '':
            typeNode.set('id', oid)
        if guid is not '':
            typeNode.set('guid', guid)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

    def finalize(self):
        """Sets the stop timestamp and total processing time"""
        self.timestampStop = datetime.datetime.now()
        self.timeProcess = self.timestampStop - self.timestampStart
        return str(self.timestampStart), str(self.timestampStop), str(self.timeProcess)

    def write(self):
        """
        Return a pretty-printed XML string for the Element. then write it out to the
        expected file.
        """
        rough_string = ET.tostring(self.project, encoding='utf8', method='xml')
        # Source: http://stackoverflow.com/a/14493981
        pretty = '\n'.join([line for line in minidom.parseString(rough_string).toprettyxml(indent="\t").split('\n') if line.strip()])
        f = open(self.logFilePath, "wb")
        f.write(pretty)
        f.close()

    def getUUID(self):
        return str(uuid.uuid4()).upper()