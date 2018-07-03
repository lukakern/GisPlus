'''
Create Test shape files
'''

import shapely.geometry as spg
import numpy as np
import os
import ogr, osr

'''
Test Polygon
'''
# create random polygon geometry
np.random.seed(None)
geometry_coll_poly = spg.collection.GeometryCollection(
    [spg.MultiPoint(
        [spg.Point(_) for _ in np.random.gamma(mid, 3, (15, 2))]
    ).convex_hull for mid in (
         [np.random.randint(0, 100) for i in range(0, 3)])]
)

'''
Test Points
'''
geometry_coll_point = spg.collection.GeometryCollection(
    [spg.MultiPoint(
        [spg.Point(_) for _ in np.random.gamma(mid, 3, (15, 2))]
    ) for mid in ([np.random.randint(0, 100) for i in range(0, 3)])])

geometry_coll_point = \
    spg.collection.GeometryCollection([geometry_coll_point[0][i]
                                       for i in
                                       range(0, len(geometry_coll_point[0]))])

'''
Test LineString
'''
geometry_coll_line = spg.collection.GeometryCollection(
    [spg.LineString([(20, 69), (1, 3)]),
     spg.LineString([(44, 60), (2, 99)]),
     spg.LineString([(45, 12), (113, 44)])])

'''
Test Mixed
'''

# create attribute values for geometries
attributes_poly = [np.random.randint(0, 255) for i in
                   range(0, len(geometry_coll_poly))]
attributes_point = [np.random.randint(0, 255) for i in
                    range(0, len(geometry_coll_point))]
attributes_line = [np.random.randint(0, 255) for i in
                   range(0, len(geometry_coll_line))]

# join geometry and their attributes
geom_attr_poly = list(zip(geometry_coll_poly, attributes_poly))
geom_attr_point = list(zip(geometry_coll_point, attributes_point))
geom_attr_line = list(zip(geometry_coll_line, attributes_line))


path = input("Please enter a path for test files: ")
os.chdir(path)


'''
Polygon save
'''

polygons = []
polygons.append([ogr.CreateGeometryFromWkt(str(geometry_coll_poly[i])) for i in
                 range(0, len(geometry_coll_poly))])

folder_poly = 'test_polygons'
filepath = os.path.join(path, folder_poly, 'tst_polygons.shp')

if not os.path.exists(folder_poly):
    os.mkdir(folder_poly)

drv = ogr.GetDriverByName("ESRI Shapefile")

if os.path.exists(filepath):
    drv.DeleteDataSource(filepath)

src = drv.CreateDataSource(filepath)

reference = osr.SpatialReference()
reference.ImportFromEPSG(25823)

# create layer
lyr = src.CreateLayer("Polygons", reference, geom_type=ogr.wkbPolygon)

attributeField = ogr.FieldDefn("ATTRIBUTE", ogr.OFTInteger)
lyr.CreateField(attributeField)

defn = lyr.GetLayerDefn()

for polygon, attribute in zip(polygons[0], attributes_poly):
    # create feature using the layer definition
    feature = ogr.Feature(defn)

    # add the geometry and fill the fields
    feature.SetGeometry(polygon)
    feature.SetField("ATTRIBUTE", attribute)

    # create the feature and set to None
    lyr.CreateFeature(feature)
    feature = None

lyr = None
src = None

'''
Points save
'''

points = []
points.append([ogr.CreateGeometryFromWkt(str(geometry_coll_point[i])) for i in
               range(0, len(geometry_coll_point))])

folder_point = 'test_points'
filepath = os.path.join(path, folder_point, 'tst_points.shp')

if not os.path.exists(folder_point):
    os.mkdir(folder_point)

drv = ogr.GetDriverByName("ESRI Shapefile")

if os.path.exists(filepath):
    drv.DeleteDataSource(filepath)

src = drv.CreateDataSource(filepath)

reference = osr.SpatialReference()
reference.ImportFromEPSG(25823)

# create layer
lyr = src.CreateLayer("Points", reference, geom_type=ogr.wkbPoint)

attributeField = ogr.FieldDefn("ATTRIBUTE", ogr.OFTInteger)
lyr.CreateField(attributeField)

defn = lyr.GetLayerDefn()

for point, attribute in zip(points[0], attributes_point):
    # create feature using the layer definition
    feature = ogr.Feature(defn)

    # add the geometry and fill the fields
    feature.SetGeometry(point)
    feature.SetField("ATTRIBUTE", attribute)

    # create the feature and set to None
    lyr.CreateFeature(feature)
    feature = None

lyr = None
src = None


'''
Lines
'''

lines = []
lines.append([ogr.CreateGeometryFromWkt(str(geometry_coll_line[i])) for i in
              range(0, len(geometry_coll_line))])

folder_lines = 'test_lines'
filepath = os.path.join(path, folder_lines, 'tst_lines.shp')

if not os.path.exists(folder_lines):
    os.mkdir(folder_lines)

drv = ogr.GetDriverByName("ESRI Shapefile")

if os.path.exists(filepath):
    drv.DeleteDataSource(filepath)

src = drv.CreateDataSource(filepath)

reference = osr.SpatialReference()
reference.ImportFromEPSG(25823)

# create layer
lyr = src.CreateLayer("LINES", reference, geom_type=ogr.wkbLineString)
attributeField = ogr.FieldDefn("ATTRIBUTE", ogr.OFTInteger)
lyr.CreateField(attributeField)

defn = lyr.GetLayerDefn()

for line, attribute in zip(lines[0], attributes_line):
    # create feature using the layer definition
    feature = ogr.Feature(defn)

    # add the geometry and fill the fields
    feature.SetGeometry(line)
    feature.SetField("ATTRIBUTE", attribute)

    # create the feature and set to None
    lyr.CreateFeature(feature)
    feature = None

lyr = None
src = None



