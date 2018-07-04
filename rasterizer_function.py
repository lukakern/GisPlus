from typing import List, Any, Union

import fiona
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as spg
from shapely.geometry import shape
import skimage as sk
from skimage import external, io, exposure


def rasterizer(
        filepath="../../pyCharmTest/venv/data/muenster_stands/stands.shp",
        pixels=100,
        buffer=10,
        outputname="output.tiff"):
    '''
    description of function

    buffer: Please enter a buffer value for the minimum bounding box:
    resolution: Please enter a value for the resolution (the lower the higher is the resolution):
    :return:
    '''

    ## shapely is only abount geometry, it does not deal with any coordinate reference system (CRS)!
    # now use the shape function of Shapely
    global step
    geometry_coll = spg.collection.GeometryCollection(
        [shape(pol['geometry']) for pol in fiona.open(filepath)]
    )

    # create attribute values for geometries
    # attributes = [np.random.randint(0, 255) for i in
    # range(0, len(geometry_coll))]

    # join geometry and their attributes
    # geom_attr = list(zip(geometry_coll, attributes))

    # cornerstones of bounding box
    bbox = geometry_coll.bounds

    x_range = abs(round(bbox[2]) - round(bbox[1]))
    #y_range = round(bbox[3]) - round(bbox[1])

    resolution = x_range / pixels
    x_range = round(x_range / resolution) * resolution

    # implemented buffer frame around the geometries
    bbox_plus_buffer = []
    #  implemented buffer
    [bbox_plus_buffer.append(bbox[i] - float(buffer*resolution)) for i in (0, 1)]
    [bbox_plus_buffer.append(bbox[i] + float(buffer*resolution)) for i in (2, 3)]

    x_min = round(bbox_plus_buffer[0] / resolution) * resolution
    x_max = round(bbox_plus_buffer[2] / resolution) * resolution
    y_min = round(bbox_plus_buffer[1] / resolution) * resolution
    y_max = round(bbox_plus_buffer[3] / resolution) * resolution

    # create a grid for the geometry bounding box
    geom_y, geom_x = np.mgrid[y_min:y_max:float(resolution),
                     x_min:x_max:float(resolution)]
    # create a point geometry for every grid cell
    geom_pixels = []
    for i in range(0, len(geom_x[:, 1])):
        for j in range(0, len(geom_y[1, :])):
            geom_pixels.append(spg.Point([geom_x[i, j], geom_y[i, j]]))


    # check if the pixel/point lies within one of the geometries (separately)
    within_list = []
    for i in range(0, len(geometry_coll)):
        if isinstance(geometry_coll[i], spg.polygon.Polygon):
            step = [pixel.within(geometry_coll[i]) for pixel in geom_pixels]
        if isinstance(geometry_coll[i], spg.point.Point):
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
        if (isinstance(geometry_coll[i], spg.linestring.LineString)):
            step = [pixel.within(geometry_coll[i].buffer(float(resolution)))
                    for pixel in geom_pixels]
        print(i)
        within_list.append(step)

    # check for geometry attribute
    for i in range(0, len(geometry_coll)):
        print("Geometry {} contains attribute value: {}".format(i, np.unique(
            within_list[i])[-1]))

    # join separate within_list 's. If overlapping: add attribute values
    for i in range(1, len(geometry_coll)):
        for j in range(0, len(within_list[0])):
            within_list[0][j] = within_list[0][j] + within_list[i][j]

    # write in single list
    within_list_sum = within_list[0]  # type: Union[Union[List[bool], List[Union[bool, Any]]], Any]

    ## set radiometric resolution to 8bit
    within_list_sum = np.round_(
        255 * (np.true_divide(within_list_sum, max(within_list_sum))))

    # check for geometry attributes
    print("Attribute values of geometries: ", np.unique(within_list_sum))

    # create sublists every nth step
    size = len(geom_x[1, :])
    within_list_sub = []
    for i in range(0, len(within_list_sum), size):
        within_list_sub.append(within_list_sum[i:i + size])

    # create numpy array from the prepared list
    within_array = np.array(within_list_sub, dtype='uint8')

    # flip array for correct presentation
    flipped_array = np.flipud(within_array)
    # plt.imshow(flipped_array, plt.cm.gray)
    # plt.show()

    ##write image data to tiff file
    sk.external.tifffile.imsave(outputname, flipped_array)


#rasterizer()
rasterizer(filepath="../test_points/tst_points.shp",
           pixels=100,
           buffer = 10,
           outputname="points_tst.tiff")
