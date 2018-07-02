
'''
Hello Hello
'''


import shapely.geometry as spg
import numpy as np
import matplotlib.pyplot as plt



#create random polygon geometry
np.random.seed(None)
geometry_coll = spg.collection.GeometryCollection(
    [spg.MultiPoint(
        [spg.Point(_) for _ in np.random.gamma(mid, 3, (15, 2))]
    ).convex_hull for mid in(
        [np.random.randint(0, 100) for i in range(0, 3)])]
)

# create attribute values for geometries
attributes = [np.random.randint(0, 255) for i in range(0, len(geometry_coll))]

# join geometry and their attributes
geom_attr = list(zip(geometry_coll, attributes))

# cornerstones of bounding box
bbox = geometry_coll.bounds

# implemented buffer frame around the geometries
buffer = input(
    "Please enter a buffer value for the minimum bounding box: ")

bbox_plus_buffer = []  # implemented buffer
[bbox_plus_buffer.append(bbox[i] - float(buffer)) for i in (0, 1)]
[bbox_plus_buffer.append(bbox[i] + float(buffer)) for i in (2, 3)]

x_min = round(bbox_plus_buffer[0])
x_max = round(bbox_plus_buffer[2])
y_min = round(bbox_plus_buffer[1])
y_max = round(bbox_plus_buffer[3])

# create a grid for the geometry bounding box
resolution = input(
    "Please enter a value for the resolution (the lower the higher is the resolution): ")
geom_y, geom_x = np.mgrid[y_min:y_max:float(resolution),
                 x_min:x_max:float(resolution)]

# create a point geometry for every grid cell
geom_pixels = []
for i in range(0, len(geom_x[:, 1])):
    for j in range(0, len(geom_x[1, :])):
        geom_pixels.append(spg.Point([geom_x[i, j], geom_y[i, j]]))

# check if the pixel/point lies within one of the geometries (separately)
within_list = []
for i in range(0, len(geometry_coll)):
    step = [pixel.within(geometry_coll[i]) for pixel in geom_pixels]
    # step = [pixel.within(geometry_coll[i]) for pixel in geom_pixels]
    within_list.append(step)

len(within_list[0])

# for every True in of the within list the attribute of the geometry is taken
for i in range(0, len(geometry_coll)):
    for j in range(0, len(within_list[0])):
        if within_list[i][j] == 1:
            within_list[i][j] = geom_attr[i][1]

# check for geometry attribute
for i in range(0, len(geometry_coll)):
    print("Geometry {} contains attribute value: {}".format(i, np.unique(
        within_list[i])[-1]))

# join separate within_list 's. If overlapping: add attribute values
for i in range(1, len(geometry_coll)):
    for j in range(0, len(within_list[0])):
        within_list[0][j] = within_list[0][j] + within_list[i][j]

# write in single list
within_list_sum = within_list[0]

# check for geometry attributes
print("Attribute values of geometries: ", np.unique(within_list_sum))

# create sublists every nth step
size = len(geom_x[1, :])
within_list_sub = [within_list_sum[i:i + size] for i in
                   range(0, len(within_list_sum), size)]

# create numpy array from the prepared list
within_array = np.array(within_list_sub, dtype='uint8')

# flip array for correct presentation
flipped_array = np.flipud(within_array)
plt.imshow(flipped_array, plt.cm.gray)
plt.show()

