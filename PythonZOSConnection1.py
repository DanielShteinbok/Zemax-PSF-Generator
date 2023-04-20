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

def getPSFValue(fieldnum, ImageDelta=3, callback=lambda x:x, ImageSampleSize=ZOSAPI.Analysis.SampleSizes.S_64x64, PupilSampleSize=ZOSAPI.Analysis.SampleSizes.S_256x256, wavelength=2, 
        Normalize=False, setNormalize=False):
    # callback is passed the results, and does whatever you want it to do. I will use this to call GetTextFile.
    # Open the Huygens PSF analysis
    huygens_psf = TheSystem.Analyses.New_HuygensPsf()

    # Get analysis settings
    huygens_psf_settings = huygens_psf.GetSettings()
    # MY ADDITION: Cast huygens_psf_settings
    #huygens_psf_settings = typing.cast(huygens_psf_settings, ZOSAPI.Analysis.Settings.Psf.IAS_HuygensPsf)

    # set field number
    huygens_psf_settings.Field.SetFieldNumber(int(fieldnum))

    # set image sample size
    huygens_psf_settings.ImageSampleSize = ImageSampleSize

    # set the pupil sampling
    huygens_psf_settings.PupilSampleSize = PupilSampleSize

    # set the wavelength
    huygens_psf_settings.Wavelength.SetWavelengthNumber(wavelength)

    # set image delta (pixel size)
    huygens_psf_settings.ImageDelta = ImageDelta

    # set the normalization, only if setNormalize is True
    # this seems really silly to do, but it looks like there is some default setting
    # that differs from both True and False for Normalize
    if bool(setNormalize):
        huygens_psf_settings.Normalize = bool(Normalize)

    # Get field number
    field_number = huygens_psf_settings.Field.GetFieldNumber()

    # Print field number
    print('Field number: ' + str(field_number))

    # MY ADDITION
    huygens_psf.ApplyAndWaitForCompletion()
    results = huygens_psf.GetResults()
    allValues = results.GetDataGrid(0).Values

    # call the callback
    print("calling callback")
    print(callback(results))

    # Close the analysis
    huygens_psf.Close()
    return allValues
    #return results

#print(np.asarray(allValues)[0,0])
# TODO: iterate element by element, dump into CSV
# TODO: take CLI arguments for num_fields, csv_dir

import sys # for access to argv
import psf_to_csv as to_csv # the module to output as csv

# HORRIBLE way of doing things, but dead simple for now.
# path to the directory in which this file resides, such that afterward you can use a relative path
path_to_here = os.getcwd()
print(path_to_here)

# if no arguments are given, print usage instructions
if len(sys.argv) == 1:
    print("For usage instructions, see README.md")
# if there is only one argument given (len(argv)==2) that argument is the name of a csv to create.
elif len(sys.argv) == 2:
    csvpath = sys.argv[1]
    #results = getPSFValue(1)
    #results.GetDataGrid(0).Values
    #to_csv.grid_to_csv(results.GetDataGrid(0).Values, csvpath)
    callback = lambda results: results.GetTextFile(path_to_here + "\\textdump.txt")
    to_csv.grid_to_csv(getPSFValue(1, callback=callback), csvpath, dims=(64,64))


#elif len(sys.argv) == 4:
# Thus, we have either 2 or 3 arguments
else:
    kwargs = {}
    num_fields = TheSystem.SystemData.Fields.NumberOfFields
    metafile_path = sys.argv[2]
    #elif len(sys.argv) == 4:
        #num_fields = sys.argv[2]
        #metafile_path = sys.argv[3]
    # first argument is the path to the directory into which to dump all CSVs
    # EDIT: previously, we didn't want too many arguments
    # now, we want to use the additional arguments as arguments for the extraction of the PSFs
    # Also, we no longer want to have to ever specify the number of fields to examine.
    if len(sys.argv) > 3:
        #raise ValueError("Too many arguments")
        # Crazy CLI! arguments will be like: <argname> <argval> ...
        # But the first 3 arguments will be respectively: __name__, <dirpath>, <metapath>
        # so that means we must have an odd number of arguments
        if len(sys.argv) % 2 != 1:
            raise ValueError("Must have arguments passed as [<argname> <argval>] ... You either have a name or value that is missing")
        # collect all the values that we want to pass to getPSFValue
        i = 3
        while i+1 < len(sys.argv):
            kwargs[sys.argv[i]] = sys.argv[i+1]
            i += 2

    dirpath = sys.argv[1]
    # second argument is the number of PSFs
    # the third argument is the path to the meta file

    # the dictionary that will store all the meta info
    meta_dict = []

    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    for psfnum in range(1, int(num_fields)+1):
        # generate the name of the new CSV
        csvpath = dirpath.rstrip("/") + "/F" + str(psfnum) + ".csv"
        #to_csv.grid_to_csv(getPSFValue(psfnum), csvpath)
        #to_csv.grid_to_csv(getPSFValue(psfnum, ImageDelta=0, ImageSampleSize=ZOSAPI.Analysis.SampleSizes.S_64x64), csvpath, dims=(64,64))
        #to_csv.grid_to_csv(getPSFValue(psfnum, ImageDelta=0), csvpath)
        # TODO: results.GetTextFile() and then read that file and put the important info into a list with the field number.
        # Then, put that list into a csv.
        # For the above TODO: create a textdump.txt in the current working directory,
        # then read that textdump to get the center coordinates
        # the latter is on line 16, and looks like:
        # Center coordinates   :   [num], [num] Millimeters
        callback_dump_text = lambda results: results.GetTextFile(path_to_here + "\\textdump.txt")
        to_csv.grid_to_csv(getPSFValue(psfnum, callback=callback_dump_text, **kwargs), csvpath, dims=(64,64))
        # textdump should have been written
        field_x = TheSystem.SystemData.Fields.GetField(psfnum).X
        field_y = TheSystem.SystemData.Fields.GetField(psfnum).Y
        # generate the meta row
        meta_dict.append(
                to_csv.textdump_to_meta(path_to_here + "\\textdump.txt", psfnum, field_x, field_y)
                )

    with open(metafile_path, 'w', newline='') as metafile:
        fieldnames = ["Field Number","X (mm)","Y (mm)","X image (px)","Y image (px)"]
        writer = csv.DictWriter(metafile, fieldnames=fieldnames)
        writer.writeheader()
        for row in meta_dict:
            writer.writerow(row)


