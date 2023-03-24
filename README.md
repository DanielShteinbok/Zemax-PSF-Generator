# PSF Generator
Code using the ZOS-API to generate a bunch of point-spread functions from a bunch of fields (different points on the object).
For use with [my version of the Waller-Lab's MultiWienerNet](https://github.com/DanielShteinbok/MultiWienerNet).

The original MultiWienerNet can be found [here](https://github.com/Waller-Lab/MultiWienerNet), but the difference is that
my fork is meant to work with CSVs rather than MATLAB .mat files. This PSF generator will produce CSV files.

## Usage:
Open up the model in question in Zemax. Click `Programming > Interactive Session`.

Open up a terminal emulator, run:
`python PythonZOSConnection1.py <dirpath> <fieldcount> <metapath>`

### Arguments:
`dirpath`: the path to the directory where the PSF files will be saved

`fieldcount`: the number of fields

`metapath`: the path to the metafile

### Example usage:
`python PythonZOSConnection1.py psfs_probe/ 29 metafile_probe.csv`

# Field Maker
This is a script to create a whole bunch of fields for which we may later want to sample PSFs with
`PythonZOSConnection1.py`. It can also tell you how many fields you currently have.

## Usage:
As with the other script, ensure you have the model open in Zemax and start the Interactive Session.

### Get number of fields:
To just figure out how many fields you have, in a terminal emulator and in the proper conda environment, run:

`python field_maker.py`

This should spit out a number.

### Create a bunch of fields:
The script could be used to create a whole bunch of fields points in the object plane, because this
is tedious to do manually. It assumes that you currently have some number of fields in a line
stretching from the center of your object plane (inclusive, so you already have a field in the center)
directly upward.

Before running the script to create new fields, you should ensure that your fields are currently laid
out correctly. See the [confluence documentation](https://inscopix.atlassian.net/wiki/spaces/~630ce20662fe1e6eac6bdb1f/pages/2854649996/Zemax+PSF+Generator) for details.
Next, in the terminal emulator, run:
`python filed_maker.py [number of rotations]`
