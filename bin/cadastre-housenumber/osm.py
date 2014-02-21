#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with it. If not, see <http://www.gnu.org/licenses/>.


"""

OSM file Parser/Writer

"""

import sys
import os.path
import xml.sax.saxutils
import xml.parsers.expat

class Osm(object):
    def __init__(self, attrs):
        self.attrs = {}
        self.attrs.update(attrs);
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.min_node_id = 0;
        self.min_way_id = 0;
        self.min_relation_id = 0;
        self.bounds = []
        if not self.attrs.has_key('version'):
          self.attrs['version'] = '0.6'
        if not self.attrs.has_key('generator'):
          self.attrs['generator'] = os.path.basename(sys.argv[0])
    def add_node(self, node):
        if (node.attrs.has_key("id")):
            id = int(node.attrs["id"])
            assert(not self.nodes.has_key(id))
        else:
            id = self.min_node_id - 1
            node.attrs["id"] = str(id)
        self.min_node_id = min(self.min_node_id, id)
        self.nodes[id] = node
    def add_way(self, way):
        if (way.attrs.has_key("id")):
            id = int(way.attrs["id"])
            assert(not self.ways.has_key(id))
        else:
            id = self.min_way_id - 1
            way.attrs["id"] = str(id)
        self.min_way_id = min(self.min_way_id, id)
        self.ways[id] = way
    def add_relation(self, relation):
        if (relation.attrs.has_key("id")):
            id = int(relation.attrs["id"])
            assert(not self.relations.has_key(id))
        else:
            id = self.min_relation_id - 1
            relation.attrs["id"] = str(id)
        self.min_relation_id = min(self.min_relation_id, id)
        self.relations[id] = relation
    def bbox(self):
        minlon = min([float(b["minlon"]) for b in self.bounds])
        minlat = min([float(b["minlat"]) for b in self.bounds])
        maxlon = max([float(b["maxlon"]) for b in self.bounds])
        maxlat = max([float(b["maxlat"]) for b in self.bounds])
        return minlon,minlat,maxlon,maxlat
    def set_bbox(self,bbox):
        minlon,minlat,maxlon,maxlat = bbox
        self.bounds.append({
          "minlon": str(minlon),
          "minlat": str(minlat),
          "maxlon": str(maxlon),
          "maxlat": str(maxlat)})

class Node(object):
    def __init__(self, attrs,tags=None):
        self.attrs = attrs
        self.tags = tags or {}
    def id(self):
        return int(self.attrs["id"])

class Way(object):
    def __init__(self, attrs,tags=None):
        self.attrs = attrs
        self.tags = tags or {}
        self.nodes = []
    def add_node(self, node):
        if type(node) == Node:
            self.nodes.append(node.id())
        else:
            assert((type(node) == str) or (type(node) == unicode) or (type(node) == int))
            self.nodes.append(int(node))
    def id(self):
        return int(self.attrs["id"])
        

class Relation(object):
    def __init__(self, attrs,tags=None):
        self.attrs = attrs
        self.tags = tags or {}
        self.members = []
    def add_member(self, member, role=""):
        if type(member) == dict:
            attrs = member
        else:
            attrs = {}
            if type(member) == Node:
                attrs['type'] = 'node'
            elif type(member) == Way:
                attrs['type'] = 'way'
            elif type(member) == Relation:
                attrs['type'] = 'relation'
            else:
                raise Exception("unknown member type")
            attrs['ref'] = str(member.id())
        if role: attrs['role'] = role
        self.members.append(attrs)
    def id(self):
        return int(self.attrs["id"])

class OsmParser(object):
    def __init__(self):
        self.parser = xml.parsers.expat.ParserCreate("utf-8")
        assert(self.parser.SetParamEntityParsing(
            xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER))
        self.parser.buffer_text = True
        self.parser.CharacterDataHandler = self.handle_char_data
        self.parser.StartElementHandler = self.handle_start_element
        self.parser.EndElementHandler = self.handle_end_element
    def parse(self, filename):
        self.filename = filename
        self.osm = None
        self.parser.ParseFile(open(filename))
        return self.osm
    def parse_stream(self, stream, name=""):
        self.filename = name
        self.osm = None
        self.parser.ParseFile(stream)
        return self.osm
    def parse_data(self, data, name=""):
        self.filename = name
        self.osm = None
        self.parser.Parse(data)
        return self.osm
    def handle_start_element(self,name, attrs):
        if name == "osm":
            osm = Osm(attrs)
            self.osm = osm
            self.current = None
        elif name == "note":
            #TODO
            pass
        elif name == "meta":
            #TODO
            pass
        elif name == "bounds":
            self.osm.bounds.append(attrs)
        elif name == "node":
            node = Node(attrs);
            self.osm.add_node(node)
            self.current = node
        elif name == "way":
            way = Way(attrs)
            self.osm.add_way(way)
            self.current = way
        elif name == "nd":
            ref = int(attrs["ref"])
            way = self.current
            way.add_node(ref)
        elif name == "tag":
            self.current.tags[attrs["k"]] = attrs["v"];
        elif name == "relation":
            relation = Relation(attrs)
            self.osm.add_relation(relation)
            self.current = relation
        elif name == "member":
            member = attrs
            relation = self.current
            relation.add_member(member)
        else:
            raise Exception("ERROR: unknown tag <"+name+"> in file " 
                    + self.filename + "\n")
    def handle_end_element(self,name):
        pass
    def handle_char_data(self,data):
        pass
 
class OsmWriter(object):
    def __init__(self, osm):
        self.osm = osm
    def write_to_file(self, filename):
        self.output = open(filename, mode="w")
        self.write()
        self.output.close()
    def write_to_stream(self, stream):
        self.output = stream
        self.write()
    def write(self):
        osm = self.osm
        output = self.output
        output.write("<?xml version='1.0' encoding='UTF-8'?>\n");
        output.write("<osm" + self.attrs_str(osm.attrs) + ">\n");
        for bounds in osm.bounds:
            output.write("\t<bounds" + self.attrs_str(bounds) + "/>\n");
        for node in osm.nodes.itervalues():
            if len(node.tags):
                output.write("\t<node" + self.attrs_str(node.attrs) + ">\n");
                self.write_tags(node.tags)
                output.write("\t</node>\n");
            else:    
                output.write("\t<node" + self.attrs_str(node.attrs) + "/>\n");
        for way in osm.ways.itervalues():
            output.write("\t<way" + self.attrs_str(way.attrs) + ">\n");
            for ref_node in way.nodes:
                output.write('\t\t<nd ref="' + str(ref_node) + '"/>\n');
            self.write_tags(way.tags)
            output.write("\t</way>\n");
        for relation in osm.relations.itervalues():
            output.write("\t<relation" 
                + self.attrs_str(relation.attrs) + ">\n");
            self.write_tags(relation.tags)
            for member in relation.members:
                output.write('\t\t<member' + self.attrs_str(member) + "/>\n");
            output.write("\t</relation>\n");
        output.write("</osm>\n");
    def attrs_str(self, attrs):
        return ("".join([' ' + key + '=' + xml.sax.saxutils.quoteattr(value)
            for key,value in attrs.iteritems()])).encode("utf-8")
    def write_tags(self, tags):
        for key,value in tags.iteritems():
            value = xml.sax.saxutils.quoteattr(value)
            self.output.write(('\t\t<tag k="' + key + '" v=' + value +'/>\n').encode("utf-8"))


