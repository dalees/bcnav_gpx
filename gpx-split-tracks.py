#!/usr/bin/python

import argparse
import os
import sys
import time

import xml.etree.ElementTree as ET

class TopoGrafixGPX(object):
    # Namespaces within the XML doc
    namespace = 'http://www.topografix.com/GPX/1/1'

    def __init__(self, file):
        ET.register_namespace('topografix', "http://www.topografix.com/GPX/Private/TopoGrafix/0/1")
        self.source_file = file
        filepath = os.path.abspath(file)
        self.target_dir = os.path.dirname(filepath)
        self.load()

    def _get_text(self, track_node, node_name):
        name_node = track_node.find(self._node(node_name))
        try:
            content = name_node.text
        except AttributeError:
            content = None
        if content == 'None':
            content = None
        return content

    def _node(self, name):
        return '{%s}%s' % (self.namespace, name)

    def load(self):
        # open arg1 into a dom
        context = ET.iterparse(self.source_file, events=("end", ))
        self.root = None
        fixup_tags = [
            self._node('wpt'),
            self._node('trkpt'),
            self._node('gpx')
            ]
        for event, elem in context:
            # clean up attribute namespace issues with each node
            if elem.tag in fixup_tags:
                for key, value in elem.attrib.iteritems():
                    if not key.startswith('{'):
                        elem.attrib.pop(key)
                        elem.attrib[self._node(key)] = value
            # Grab the root element for later use
            if elem.tag == self._node('gpx'):
                self.root = elem

    def save(self):
        # Go through each track in the DOM and write a new file for each
        for track in self.root.iter(self._node('trk')):
            track_number = self._get_text(track, 'number')
            track_name = self._get_text(track, 'name')
            track_descr = self._get_text(track, 'desc')
            if track_descr is None:
                track_file = '%s\\%s.gpx' % (self.target_dir, track_name)
            else:
                track_file = "%s\\%s-%s.gpx" % (self.target_dir, track_name, track_descr)
            print "Creating track %s" % track_file
            # Create new tree from this track and the root attribs
            trackroot = ET.Element(self._node('gpx'))
            trackroot.attrib = self.root.attrib
            trackroot.append(track)
            ET.ElementTree(trackroot).write(
                track_file,
                xml_declaration=True,
                encoding='utf-8',
                method="xml",
                default_namespace=self.namespace
                )

def file_arg(path):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError('Path to a real file expected.')
    return path

parser = argparse.ArgumentParser(description='Split a Backcountry Navigator file into individual tracks.')
parser.add_argument(
    'gpx_path',
    type=file_arg,
    nargs='+'
    )
args = parser.parse_args()

try:
    for path in args.gpx_path:
        print "Reading GPX file '%s" % path
        gpx = TopoGrafixGPX(path)
        gpx.save()
except ET.ParseError:
    print "\tFailed to parse GPX file '%s'" % path
    print "\tIs this an exported trip from Backcountry Navigator?"

print "All done. Window will close in 5 seconds."
time.sleep(5)
