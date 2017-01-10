import os
from shutil import copyfile

# constants
RS_SUBDIRS = ["Inputs", "Realizations"] # directories in the Riverscape Project root
RS_OUTDIRS = ["Polystat", "Predict"] # directories storing Riverscape realization outputs


def writeRSDirs(rs_root, RS_SUBDIRS, RS_OUTDIRS):
    """Writes optional Riverscape project file folders"""
    if not os.path.exists(rs_root):
        os.remove(rs_root)
    for subdir in RS_SUBDIRS:
        os.mkdir(os.path.join(rs_root, subdir))
    for outdir in RS_OUTDIRS:
        os.mkdir(os.path.join(rs_root, RS_SUBDIRS[1], outdir))


def exportRSFiles(data_file, rs_root, subdir_index = '', outdir_index = ''):
    """Exports data files to Riverscapes project directories"""
    if subdir_index and outdir_index: # i.e. the data_file is a realization/output
        copyfile(data_file, "{0}\\{1}\\{2}".format(rs_root, RS_SUBDIRS[subdir_index], RS_OUTDIRS[outdir_index]))
    elif subdir_index and outdir_index == '': #i.e. the data_file is an input
        copyfile(data_file, "{0}\\{1}".format(rs_root, RS_SUBDIRS[subdir_index]))
    else: # write to Riverscapes root directory
        copyfile(data_file, "{0}".format(rs_root))