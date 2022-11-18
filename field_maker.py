import clr, os, winreg
from itertools import islice
import csv

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
import sys
import math

fields = TheSystem.SystemData.Fields

if len(sys.argv) == 1:
    # if no arguments are passed, print the number of fields
    print("Number of fields: ", fields.NumberOfFields)
elif len(sys.argv) == 2:
    # if one argument is passed, it should be an integer corresponding to the number of times 
    # which we want to rotate all the fields around the center of the FOV
    # that is, if we pass n we should end up with n times as many fields as we started with,
    # and they should be evenly separated in terms of angle

    # d_angle is the angle between lines of fields, in radians
    d_angle = 2*math.pi/int(sys.argv[1])

    # iterate through all angles displaced from the starting line of fields
    # we repeat the contents of this for-loop one less time than 
    # the number passed as an argument, since we already have one line of fields
    first_field_number = fields.NumberOfFields
    for i in range(1, int(sys.argv[1])):
        # iterate through each field, I'm assuming they are in a vertical line
        # this means that all the x-coordinates are 0
        # and all the y-coordinates are >= 0
        for fieldNum in range(1, first_field_number+1):
            toCopy = fields.GetField(fieldNum)
            # we are measuring the angle clockwise, starting from 12:00,
            # which is the positive y-axis
            # this means that x is sin, and y is cos
            r = math.sqrt(toCopy.X**2 + toCopy.Y**2)
            if r == 0:
                continue
            x_out = r*math.sin(i*d_angle)
            y_out = r*math.cos(i*d_angle)
            fields.AddField(x_out, y_out, toCopy.Weight)
