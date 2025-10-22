# edit at 2024-04-22
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
import math
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon

# def get_spec_of_points(points):
#     x, y = zip(*points)
#     bbox =  min(x), min(y), max(x), max(y)
#     center = bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2
#     width = bbox[2] - bbox[0]
#     height = bbox[3] - bbox[1]
#     recommended_zoom = 6
#     if width > 2.0:
#         recommended_zoom = 12
#     elif width > 1.5:
#         recommended_zoom = 11
#     elif width > 1.0:
#         recommended_zoom = 10
#     elif width > 0.5:
#         recommended_zoom = 9
#     elif width > 0.25:
#         recommended_zoom = 8
#     elif width > 0.195:
#         recommended_zoom = 7
#     elif width > 0.125:
#         recommended_zoom = 6
#     elif width > 0.0625:
#         recommended_zoom = 5

#     return {
#         'bbox': bbox, 'center': center,
#         'width': width, 'height': height,
#         'zoom': recommended_zoom
#     }

# def center_str(geom):
#     return f'{geom.centroid.x:.6f},{geom.centroid.y:.6f}'

# def merge_geoms(geoms):

#     to_merge = [x['geometry']['coordinates'][0] for x in geoms]
#     shapes = {
#         'coordinates': to_merge,
#         'type': 'MultiPolygon'
#     }

#     return GEOSGeometry(json.dumps(shapes), srid=4326)

# def get_outermost_points(points):
#     polygon = Polygon(points + [points[0]])
#     center = polygon.centroid
#     points = sorted(points, key=lambda x: x.distance(center))
#     return points[-1]

# def bbox_to_polygon(bbox):
#     left, bottom, right, top = bbox
#     return f'POLYGON (({left} {top}, {right} {top}, {right} {bottom}, {left} {bottom}, {left} {top}))'


#             # bbox = grid3.geom.extent
#             # parent_left, parent_bottom, parent_right, parent_top = bbox

#             # x_grad = (parent_right - parent_left) / divider
#             # y_grad = (parent_top - parent_bottom) / divider

#             # for x_step in range(divider):
#             #     for y_step in range(divider):

#             #         left = parent_left + x_grad * x_step
#             #         right = left + x_grad
#             #         bottom = parent_bottom + y_grad * y_step
#             #         top = bottom + y_grad

#             #         grid = grid4_models.Grid4()
#             #         grid.order = f'{grid3.id}|{x_step},{y_step}'
#             #         grid.geom = f'MULTIPOLYGON ((({left} {top}, {right} {top}, {right} {bottom}, {left} {bottom}, {left} {top})))'

#             #         grid.grid3 = grid3.id
#             #         grid.save()

# def getCoordsM2(coordinates):
#     d2r = 0.017453292519943295  # Degrees to radiant
#     area = 0.0
#     for coord in range(0, len(coordinates)):
#         point_1 = coordinates[coord]
#         point_2 = coordinates[(coord + 1) % len(coordinates)]
#         area += ((point_2[0] - point_1[0]) * d2r) *\
#             (2 + math.sin(point_1[1] * d2r) + math.sin(point_2[1] * d2r))
#     area = area * 6378137.0 * 6378137.0 / 2.0
#     return math.fabs(area)

# def getGeometryM2(geometry):
#     area = 0.0
#     if geometry.num_coords > 2:
#         # Outer ring
#         area += getCoordsM2(geometry.coords[0])
#         # Inner rings
#         for counter, coordinates in enumerate(geometry.coords):
#             if counter > 0:
#                 area -= getCoordsM2(coordinates)
#     return area