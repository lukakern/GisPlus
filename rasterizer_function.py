from typing import List, Any, Union

import fiona
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as spg
from shapely.geometry import shape
import skimage as sk
from skimage import external, io, exposure
import os

def rasterizer(
        filepath,
        pixels=100,
        buffer=10,
        outputname="output.tiff",
        output_path=True,
        preview=True):
    '''
    description of function

    buffer: Please enter a buffer value for the minimum bounding box:
    resolution: Please enter a value for the resolution (the lower the higher is the resolution):
    :return:
    '''
    # collect geometries of shapefile
    geometry_coll = spg.collection.GeometryCollection(
        [shape(pol['geometry']) for pol in fiona.open(filepath)]
    )
    # cornerstones of bounding box
    bbox = geometry_coll.bounds

    x_range = abs(round(bbox[2]) - round(bbox[0]))
    y_range = abs(round(bbox[3]) - round(bbox[1]))

    # defining the resolution
    resolution = np.mean((x_range, y_range)) / pixels

    # implemented buffer frame around the geometries
    bbox_plus_buffer = []
    [bbox_plus_buffer.append(bbox[i] - float(buffer*resolution)) for i in (0, 1)]
    [bbox_plus_buffer.append(bbox[i] + float(buffer*resolution)) for i in (2, 3)]

    #
    x_min = round(bbox_plus_buffer[0] / resolution) * resolution
    x_max = round(bbox_plus_buffer[2] / resolution) * resolution
    y_min = round(bbox_plus_buffer[1] / resolution) * resolution
    y_max = round(bbox_plus_buffer[3] / resolution) * resolution

    # create a 'grid' for the geometry bounding box
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

    ## set radiometric resolution to 8bit
    within_list_sum = np.round_(
        255 * (np.true_divide(within_list_sum, max(within_list_sum))))

    # create sublists every nth step
    size = len(geom_x[1, :])
    within_list_sub = []
    for i in range(0, len(within_list_sum), size):
        within_list_sub.append(within_list_sum[i:i + size])

    # create numpy array from the prepared list
    within_array = np.array(within_list_sub, dtype='uint8')

    # flip array for correct presentation
    flipped_array = np.flipud(within_array)

    if preview == True:
        plt.imshow(flipped_array, plt.cm.gray)
        plt.show()

    if output_path == True:
        os.chdir(input('Please enter the path to the direction where the .tiff file should be saved: '))

    ##write image data to tiff file
    sk.external.tifffile.imsave(outputname, flipped_array)

#rasterizer()
rasterizer(filepath="../shps/cities.shp",
           pixels=100,
           buffer = 5,
           outputname="cities1.tiff",
           output_path=False,
           preview=False)
