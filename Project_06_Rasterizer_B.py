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


from shapely.geometry import Point, Polygon, MultiPoint, collection
import numpy as np


attributes = (5, 19, 7)
np.random.seed(None)
geometry_list = collection.GeometryCollection(
    [MultiPoint(
        [Point(*_) for _ in np.random.gamma(mid, 3, (15, 2))]
    ).convex_hull for mid in (10, 15, 40)]
)
geometry_list


list(zip(geometry_list, attributes))