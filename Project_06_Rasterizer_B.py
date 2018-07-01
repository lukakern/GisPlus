'''
Spargel Rezept:
Spargel in Bratolive angebraten
wenn anfang braun Butter dazu + Muskat + Zucker
halber brühwurfel mit wasser
weißwein essig
So viel Butter wie sonst geschmolzen (1/8 - 1/4)
Wasser dazu so wie es passt zur flüssigkeit
Salz & Pfeffer

Spargel in nassem Küchenhandtuch im Kühlschrank aufbewahren
'''


import shapely.geometry as spg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon
import gdal

attributes = [np.random.randint(0, 100) for i in range(0, 3)]

np.random.seed(1234)
geometry_coll = spg.collection.GeometryCollection(
    [spg.MultiPoint(
        [spg.Point(_) for _ in np.random.gamma(mid, 3, (15, 2))]
    ).convex_hull for mid in
     ([np.random.randint(0, 100) for i in range(0, 3)])])

geom_attr = list(zip(geometry_coll, attributes))

bbox = geometry_coll.bounds  # cornerstones of bounding box

# BUFFER ???
buffer = input(
    "Please enter a buffer value for the minimum bounding box: ")  # hardcode buffer / ask user

bbox_plus_buffer = []  # implemented buffer frame around the geometries
[bbox_plus_buffer.append(bbox[i] - float(buffer)) for i in (0, 1)]
[bbox_plus_buffer.append(bbox[i] + float(buffer)) for i in (2, 3)]

x_min = round(bbox_plus_buffer[0])
x_max = round(bbox_plus_buffer[2])
y_min = round(bbox_plus_buffer[1])
y_max = round(bbox_plus_buffer[3])

geom_y, geom_x = np.mgrid[y_min:y_max,
                 x_min:x_max]  # create a grid for the geometry bounding box

geom_pixels = []

for i in range(0, len(geom_x[1, :])):
    for j in range(0, len(geom_x[:, 1])):
        geom_pixels.append(spg.Point([geom_x[i, j], geom_y[i, j]]))

within_list = []

for i in range(0, len(geometry_coll)):  # all geometries of "vector file" 
    step = [pixel.within(geometry_coll[i]) for pixel in geom_pixels]
    within_list.append(step)

for i in range(1, len(geometry_coll)):
    for j in range(0, len(within_list[0])):
        if within_list[0][j] == 1:
            within_list[0][j] = geom_attr[0][1]
        elif within_list[i][j] == 1:
            within_list[i][j] = geom_attr[i][1]

print(np.unique(within_list[0]))  # check for geometry attribute
print(np.unique(within_list[1]))
print(np.unique(within_list[2]))

for i in range(1, len(geometry_coll)):
    for j in range(0, len(within_list[0])):
        within_list[0][j] = within_list[0][j] + within_list[i][j]

within_list_sum = within_list[0]

np.unique(within_list_sum)

size = (y_max - y_min)
within_list_sub = [within_list_sum[i:i + size] for i in
                   range(0, len(within_list_sum), size)]

within_array = np.array(within_list_sub, dtype='uint32')

flipped_array = np.flipud(within_array)
plt.imshow(flipped_array, plt.cm.gray)
plt.show()