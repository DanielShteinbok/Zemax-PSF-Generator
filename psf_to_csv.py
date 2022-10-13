import csv
def grid_to_csv(gridvals, csvpath, dims=(32,32)):
    """
    iterate through each possible position in the given dimensions,
    write this out as a csv

    gridvals: System.Double[,] the output of IA_.GetResults().GetDataGrid(0).Values

    csvpath: str the path, with filename, of the produced CSV

    dims: tuple the height and width of the PSF
    """
    with open(csvpath, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for rownum in range(dims[0]):
            rowvals = []
            for column in range(dims[1]):
                # enter column value with comma into the csv
                rowvals.append(gridvals.Get(column, rownum))
            # write out the rowvals array
            csvwriter.writerow(rowvals)
        # flush out to file; I guess csv.writer does this for each row under the hood.
