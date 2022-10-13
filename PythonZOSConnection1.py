import clr, os, winreg
from itertools import islice

# This boilerplate requires the 'pythonnet' module.
# The following instructions are for installing the 'pythonnet' module via pip:
#    1. Ensure you are running a Python version compatible with PythonNET. Check the article "ZOS-API using Python.NET" or
#    "Getting started with Python" in our knowledge base for more details.
#    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)
#
#        python -m pip install pythonnet

# determine the Zemax working directory
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)

# add the NetHelper DLL for locating the OpticStudio install folder
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper

pathToInstall = ''
# uncomment the following line to use a specific instance of the ZOS-API assemblies
#pathToInstall = r'C:\C:\Program Files\Zemax OpticStudio'

# connect to OpticStudio
success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(pathToInstall);

zemaxDir = ''
if success:
    zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory();
    print('Found OpticStudio at:   %s' + zemaxDir);
else:
    raise Exception('Cannot find OpticStudio')

# load the ZOS-API assemblies
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI.dll'))
clr.AddReference(os.path.join(os.sep, zemaxDir, r'ZOSAPI_Interfaces.dll'))
import ZOSAPI

TheConnection = ZOSAPI.ZOSAPI_Connection()
if TheConnection is None:
    raise Exception("Unable to intialize NET connection to ZOSAPI")

TheApplication = TheConnection.ConnectAsExtension(0)
if TheApplication is None:
    raise Exception("Unable to acquire ZOSAPI application")

if TheApplication.IsValidLicenseForAPI == False:
    raise Exception("License is not valid for ZOSAPI use.  Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")

TheSystem = TheApplication.PrimarySystem
if TheSystem is None:
    raise Exception("Unable to acquire Primary system")

def reshape(data, x, y, transpose = False):
    """Converts a System.Double[,] to a 2D list for plotting or post processing
    
    Parameters
    ----------
    data      : System.Double[,] data directly from ZOS-API 
    x         : x width of new 2D list [use var.GetLength(0) for dimension]
    y         : y width of new 2D list [use var.GetLength(1) for dimension]
    transpose : transposes data; needed for some multi-dimensional line series data
    
    Returns
    -------
    res       : 2D list; can be directly used with Matplotlib or converted to
                a numpy array using numpy.asarray(res)
    """
    if type(data) is not list:
        data = list(data)
    var_lst = [y] * x;
    it = iter(data)
    res = [list(islice(it, i)) for i in var_lst]
    if transpose:
        return self.transpose(res);
    return res
    
def transpose(data):
    """Transposes a 2D list (Python3.x or greater).  
    
    Useful for converting mutli-dimensional line series (i.e. FFT PSF)
    
    Parameters
    ----------
    data      : Python native list (if using System.Data[,] object reshape first)    
    
    Returns
    -------
    res       : transposed 2D list
    """
    if type(data) is not list:
        data = list(data)
    return list(map(list, zip(*data)))

print('Connected to OpticStudio')

# The connection should now be ready to use.  For example:
print('Serial #: ', TheApplication.SerialCode)

# Insert Code Here
#import typing

#psfWindow = TheSystem.Analyses.New_HuygensPsf()
#psfWindow = TheSystem.Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.HuygensPsf)
#settings = typing.cast(psfWindow.GetSettings(), ZOSAPI.Analysis.Settings.Psf.IAS_HuygensPsf)
#settings = psfWindow.GetSettings()
#field = settings.Field
#print(type(field))
#print(field)
#ield = typing.cast(field, ZOSAPI.Analysis.Settings.IAS_Field)
#field.SetFieldNumber(2)
#print(str(field.GetFieldNumber()))
#print(field.GetFieldNumber)

# Open the Huygens PSF analysis
huygens_psf = TheSystem.Analyses.New_HuygensPsf()

# Get analysis settings
huygens_psf_settings = huygens_psf.GetSettings()
# MY ADDITION: Cast huygens_psf_settings
#huygens_psf_settings = typing.cast(huygens_psf_settings, ZOSAPI.Analysis.Settings.Psf.IAS_HuygensPsf)

# Get field number
field_number = huygens_psf_settings.Field.GetFieldNumber()

# Print field number
print('Field number: ' + str(field_number))

# MY ADDITION
#huygens_psf_settings.Field.SetFieldNumber(2)
huygens_psf.ApplyAndWaitForCompletion()
print("Number of grids: ", huygens_psf.GetResults().NumberOfDataGrids)
print("Number of series: ", huygens_psf.GetResults().NumberOfDataSeries)
print(huygens_psf.GetResults().GetDataGrid(0).Values)
allValues = huygens_psf.GetResults().GetDataGrid(0).Values
#print(np.asarray(allValues)[0,0])
# TODO: iterate element by element, dump into CSV
# TODO: take CLI arguments for num_fields, csv_dir

import sys # for access to argv
import psf_to_csv as to_csv # the module to output as csv
csvpath = sys.argv[1]
to_csv.grid_to_csv(allValues, csvpath)

# Close the analysis
huygens_psf.Close()

