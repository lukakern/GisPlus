# -*- encoding: utf-8 -*-
"""Summary of script

This script is about the rasterizer function:

The function creates a raster file (.tiff) from a given shape file.

To do so the function collects the geometries defines a bounding box
around them. Within the bounding box a regular grid is generated and
points are created representing the grid cells. Then it is checked if
the grid cell/point lies within the given geometry. The boolean result
is transformed to a numpy array with a radiometric resolution of 8 bit.
This numpy array is then saved as a .tiff file.

"""

import shapely.geometry as spg
from shapely.geometry import shape
import numpy as np
import matplotlib.pyplot as plt
import fiona
import skimage as sk
import os
import gdal
import osr


def rasterizer(filepath,
               pixels=100,
               buffer=10,
               outputname="output.tiff",
               save=True,
               preview=True):

    """rasterizer function

    This function creates a raster file (.tiff) from a given shape file.

    To do so the function collects the geometries defines a bounding box
    around them. Within the bounding box a regular grid is generated and
    points are created representing the grid cells. Then it is checked if
    the grid cell/point lies within the given geometry. The boolean result
    is transformed to a numpy array with a radiometric resolution of 8 bit.
    This numpy array is then saved as a .tiff file.

    Example usage
    -------------

    rasterizer(filepath="/Users/Documents/test_polygons",
               pixels=100,
               buffer=10,
               outputname="polygons_output.tiff",
               save=True,
               preview=True)

    >> The process is running: 100% completed

    >> Please enter the path to the direction where the .tiff file should be
    saved: /Users/Documents/results

    >> The file is successfully saved



    Parameters
    ----------
    :param filepath: string
    :param pixels: integer
    :param buffer: integer
    :param outputname: string
    :param preview: boolean
    :param save: boolean
    :return preview: plot
    :return saved .tiff file: message
    """

    # collect geometries of shape file
    geometry_coll = spg.collection.GeometryCollection(
        [shape(pol['geometry']) for pol in fiona.open(filepath)]
    )
    # cornerstones of bounding box
    bbox = geometry_coll.bounds

    x_range = abs(round(bbox[2]) - round(bbox[0]))
    y_range = abs(round(bbox[3]) - round(bbox[1]))

    # defining the resolution depending on mean of x_range and y_range
    resolution = np.mean((x_range, y_range)) / pixels

    # implemented buffer frame around the geometries
    bbox_plus_buffer = []
    [bbox_plus_buffer.append(bbox[i] - float(buffer * resolution)) for i in
     (0, 1)]
    [bbox_plus_buffer.append(bbox[i] + float(buffer * resolution)) for i in
     (2, 3)]

    # define relativised minimum and maximum values of the bounding box
    x_min = round(bbox_plus_buffer[0] / resolution) * resolution
    x_max = round(bbox_plus_buffer[2] / resolution) * resolution
    y_min = round(bbox_plus_buffer[1] / resolution) * resolution
    y_max = round(bbox_plus_buffer[3] / resolution) * resolution

    # create a grid inside the geometry bounding box
    geom_y, geom_x = np.mgrid[y_min:y_max:float(resolution),
                              x_min:x_max:float(resolution)]

    # create a point geometry for every grid cell
    geom_pixels = []
    for i in range(0, len(geom_x[:, 1])):
        for j in range(0, len(geom_y[1, :])):
            geom_pixels.append(spg.Point([geom_x[i, j], geom_y[i, j]]))

    # check if the pixel/point lies within one of the geometries (separately)
    within_list = []
    if isinstance(geometry_coll[0], spg.polygon.Polygon):
        for i in range(0, len(geometry_coll)):
            step = [pixel.within(geometry_coll[i]) for pixel in geom_pixels]
            print("The process is running: {} % completed ".format(
                str(round(100 * i / len(geometry_coll), 2))))
            within_list.append(step)
    if isinstance(geometry_coll[0], spg.point.Point):
        for i in range(0, len(geometry_coll)):
            step = [
                (
                        (pixel.x > (geometry_coll[i].x - 0.5 * resolution)) &
                        (pixel.x <= (geometry_coll[i].x + 0.5 * resolution))
                ) &
                (
                        (pixel.y > (geometry_coll[i].y - 0.5 * resolution)) &
                        (pixel.y <= (geometry_coll[i].y + 0.5 * resolution))
                ) for pixel in geom_pixels
            ]

            print("The process is running: {} % completed ".format(
                str(round(100 * i / len(geometry_coll), 2))))
            within_list.append(step)
    if isinstance(geometry_coll[0], spg.linestring.LineString):
        for i in range(0, len(geometry_coll)):
            step = [pixel.within(geometry_coll[i].buffer(float(resolution)))
                    for pixel in geom_pixels]
            print("The process is running: {} % completed ".format(
                str(round(100 * i / len(geometry_coll), 2))))
            within_list.append(step)

    # join separate within_list 's. If overlapping: add attribute values
    for i in range(1, len(geometry_coll)):
        for j in range(0, len(within_list[0])):
            within_list[0][j] = within_list[0][j] + within_list[i][j]

    # write in single list
    within_list_sum = within_list[0]

    # set radiometric resolution to 8bit
    within_list_sum = np.round_(
        255 * (np.true_divide(within_list_sum, max(within_list_sum))))

    # create sublists every nth step
    size = len(geom_x[1, :])
    within_list_sub = [within_list_sum[i:i + size] for i in
                       range(0, len(within_list_sum), size)]

    # create numpy array from the prepared list
    within_array = np.array(within_list_sub, dtype='uint8')

    # flip array for correct presentation
    flipped_array = np.flipud(within_array)

    if preview:
        plt.imshow(flipped_array, plt.cm.gray)
        plt.show()

    if save:
        os.chdir(input(
            "Please enter the path where the .tiff file should be saved: "))

    # write image data to tiff file
    sk.external.tifffile.imsave(outputname, flipped_array)
    print('The file is successfully saved')

    '''

    driver = gdal.GetDriverByName("GTiff")
    outRaster = driver.Create(outputname, x_range+2*buffer, y_range+2*buffer, 1,
                              gdal.GDT_Float32)  # gdal braucht Float32
    #outRaster.SetGeoTransform(geotransform)
    outRasterSRS = osr.SpatialReference()  # source for spatialreference - object
    #outRasterSRS.ImportFromEPSG(EPSG)
    outRaster.SetProjection(
        outRasterSRS.ExportToWkt())  # takes SRS and puts it inside our canvas

     # in gdal objects we start with 1, thats why we have to write bads +1
    outRaster.GetRasterBand(1).WriteArray(flipped_array)
    outRaster.FlushCache()  ## save the image
    outRaster = None  ## release t
    '''


#rasterizer()
rasterizer(filepath="../test_lines/tst_lines.shp",
           pixels=100,
           buffer = 5,
           outputname="lines_geotiff.tiff",
           preview=False)

