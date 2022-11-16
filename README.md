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
