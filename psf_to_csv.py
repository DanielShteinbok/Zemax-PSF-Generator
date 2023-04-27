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

def textdump_to_meta(filepath, field_num, field_x, field_y, imagedelta=3):
    """
    field_x and field_y should be given in mm
    """
    with open(filepath, 'r', encoding="utf-16") as textdump:
        # iterate through the dumped file, insert gathered info into meta_dict
        #for i in range(15):
        #    textdump.readline()
        # line 12 should have the Strehl ratio
        for i in range(11):
            textdump.readline()
        strehl_ratio_text = textdump.readline()
        strehl_ratio = float(strehl_ratio_text.split(':')[1].strip())

        for i in range(3):
            textdump.readline()
        # line 16, should have the center coordinates
        # of the format:
        # Center coordinates   :   [num], [num] Millimeters
        center_text = textdump.readline()
        ct_split = center_text.split(':')
        ct_vals = ct_split[1].split()
        x_img = ct_vals[0].rstrip(',')
        x_img_px = float(x_img)*1000/imagedelta # convert from mm on image to pixels
        y_img = ct_vals[1]
        y_img_px = float(y_img)*1000/imagedelta # convert from mm on image to pixels
        if ct_split[0].split()[0] != "Center":
            raise ValueError("line 16 is not the Center coordinates")
        # the origin of the field

        return {"Field Number":field_num,
                "X (mm)":field_x, "Y (mm)":field_y,
                "X image (px)":x_img_px, "Y image (px)":y_img_px,
                "Strehl ratio":strehl_ratio}
