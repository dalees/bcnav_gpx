#!/usr/bin/python
"""
Given a kml file, calculate the total distance travelled in
nautical miles and kilometers.

Initially created to work with files downloaded from spotwalla:
https://spotwalla.com/tripViewer.php?id=7f41524a0cb0eb0eb

@author Dale Smith <dalees@gmail.com>
@date 2016-11-11
"""

from math import atan2, cos, sin, sqrt, radians
from xml.dom import minidom
import re
import collections


# adapted from haversine.py <https://gist.github.com/rochacbruno/2883505>
# see also <http://en.wikipedia.org/wiki/Haversine_formula>
def calc_distance(origin, destination):
    """great-circle distance between two points on a sphere
       from their longitudes and latitudes"""
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km. earth

    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = (sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dlon/2) * sin(dlon/2))
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = radius * c

    return d


def km_to_nm(kilometers, decimal_places=None):
    nmiles = kilometers * 0.539957
    if decimal_places:
        return round(nmiles, 2)
    return nmiles


xmldoc = minidom.parse("20161111111339-6424.kml")
kml = xmldoc.getElementsByTagName("kml")[0]
document = kml.getElementsByTagName("Document")[0]
placemarks = document.getElementsByTagName("Placemark")
regex_date = re.compile('(?P<year>[0-9]{4})\-[0-9]{2}\-[0-9]{2}')

nodes = collections.OrderedDict()
for placemark in placemarks:
    nodename = placemark.getElementsByTagName("name")[0].firstChild.data
    point = placemark.getElementsByTagName("Point")
    if not point:
        continue
    point = point[0]
    desc = placemark.getElementsByTagName("description")
    if not desc:
        continue
    result = regex_date.match(desc[0].firstChild.data)
    if not result:
        continue
    year = result.groupdict()['year']
    coords = point.getElementsByTagName("coordinates")[0].firstChild.data
    lst1 = coords.split(",")
    latitude = float(lst1[0])
    longitude = float(lst1[1])
    if year not in nodes:
        nodes[year] = []
    nodes[year].append((latitude, longitude))

total_distance = 0
for y, node_list in nodes.iteritems():
    y_distance = 0
    for i in range(1, len(node_list)):
        dist_pt = calc_distance(node_list[i-1], node_list[i])
        y_distance += dist_pt

    print "Distance for {year}: {dist_nm}nm ({dist_km} km)".format(
        dist_nm=km_to_nm(y_distance, 2),
        dist_km=round(y_distance, 2),
        year=y)
    total_distance += y_distance

# convert km into nautical miles
print "Total distance: {dist_nm}nm ({dist_km} km)".format(
    dist_nm=km_to_nm(total_distance, 2),
    dist_km=round(total_distance, 2))
