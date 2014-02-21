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
Import des pdf depuis le cadastre (http://cadastre.gouv.fr)

ATTENTION: l'utilisation des données du cadastre n'est pas libre, et ce script doit
donc être utilisé exclusivement pour contribuer à OpenStreetMap, voire 
http://wiki.openstreetmap.org/wiki/Cadastre_Fran%C3%A7ais/Conditions_d%27utilisation

Ce script est inspiré du programme Qadastre de Pierre Ducroquet
(https://gitorious.org/qadastre/qadastre2osm/)
et du script import-bati.sh
(http://svn.openstreetmap.org/applications/utils/cadastre-france/import-bati.sh)

"""

import re
import sys
import os.path
import time

from cadastre import CadastreWebsite
from mytools import write_string_to_file
from mytools import write_stream_to_file

ATTENTE_EN_SECONDE_ENTRE_DOWNLOAD = 2
# Taille dans la projection cadastrale des PDF exportés:
PDF_DOWNLOAD_BBOX_SIZE = 2000
# Nombre de pixels / unite projection cadastre des PDF exportés
PDF_DOWNLOAD_PIXELS_RATIO = 4.5

def decoupage_bbox_cadastre_forced(bbox, nb_x, x_bbox_size, x_pixels_ratio, nb_y, y_bbox_size, y_pixels_ratio):
  sys.stdout.write((u"Découpe la bbox en %d * %d [%d pdfs]\n" % (nb_x,nb_y,nb_x*nb_y)).encode("utf-8"))
  sys.stdout.flush()
  xmin, ymin, xmax, ymax = bbox
  for i in xrange(nb_x):
    x1 = xmin + i * x_bbox_size
    x2 = min(x1 + x_bbox_size, xmax)
    largeur_px = int((x2-x1) * x_pixels_ratio)
    for j in xrange(nb_y):
      y1 = ymin + j * y_bbox_size
      y2 = min(y1 + y_bbox_size, ymax)
      hauteur_px = int((y2-y1) * y_pixels_ratio)
      yield ((i,j),(x1,y1,x2,y2),(largeur_px,hauteur_px))
      if (y2 == ymax): break
    if (x2 == xmax): break

def decoupage_bbox_cadastre_size(bbox, max_size, pixels_ratio):
  """Génère un découpage de la bbox en m*n sous bbox, de taille maximale
     (max_size, max_size)
     Retourne des tuples ( (i,j), sous_bbox, (largeur_px,hauteur_px) ) 
     correspondant à la sous bbox d'indice i,j dans le découpage m*n. 
     Cette sous bbox ayant une taille en pixels size*pixels_ratio
  """
  xmin,ymin,xmax,ymax = bbox
  assert(xmin < xmax)
  assert(ymin < ymax)
  xmin = xmin - 10
  xmax = xmax + 10
  ymin = ymin - 10
  ymax = ymax + 10
  nb_x = int((xmax - xmin - 1) / max_size) + 1
  nb_y = int((ymax - ymin - 1) / max_size) + 1
  return decoupage_bbox_cadastre_forced((xmin,ymin,xmax,ymax), nb_x, max_size, pixels_ratio, nb_y, max_size, pixels_ratio)

def decoupage_bbox_cadastre_nb(bbox, nb, pixels_ratio):
  """Génère un découpage de la bbox en nb*nb sous bbox, de taille moindre.
     Retourne des tuples ( (i,j), sous_bbox, (largeur_px,hauteur_px) ) 
     correspondant à la sous bbox d'indice i,j dans le découpage nb*nb. 
     Cette sous bbox ayant une taille en pixels size*pixels_ratio
  """
  xmin,ymin,xmax,ymax = bbox
  assert(xmin < xmax)
  assert(ymin < ymax)
  xmin = xmin - 10
  xmax = xmax + 10
  ymin = ymin - 10
  ymax = ymax + 10
  x_bbox_size = (xmax - xmin) / nb
  y_bbox_size = (xmax - xmin) / nb
  return decoupage_bbox_cadastre_forced((xmin,ymin,xmax,ymax), nb, x_bbox_size, pixels_ratio, nb, y_bbox_size, pixels_ratio)

def iter_download_pdfs(cadastreWebsite, code_departement, code_commune):
    cadastreWebsite.set_departement(code_departement)
    cadastreWebsite.set_commune(code_commune)
    projection = cadastreWebsite.get_projection()
    bbox = cadastreWebsite.get_bbox()
    write_string_to_file(projection + ":%f,%f,%f,%f" % bbox, code_commune + ".bbox")
    for ((i,j), sous_bbox, (largeur,hauteur)) in \
            decoupage_bbox_cadastre_size(bbox, 
                PDF_DOWNLOAD_BBOX_SIZE, PDF_DOWNLOAD_PIXELS_RATIO):
        pdf_filename = code_commune + ("-%d-%d" % (i,j)) + ".pdf"
        bbox_filename = code_commune + ("-%d-%d" % (i,j)) + ".bbox"
        sous_bbox_str = projection + (":%f,%f,%f,%f" % sous_bbox)
        #sys.stdout.write((pdf_filename + " " + sous_bbox_str + "\n").encode("utf-8"))
        #sys.stdout.flush();
        write_string_to_file(sous_bbox_str,  bbox_filename)
        if not (os.path.exists(pdf_filename) and os.path.exists(pdf_filename + ".ok")):
            if os.path.exists(pdf_filename + ".ok"): os.remove(pdf_filename + ".ok")
            write_stream_to_file(
              cadastreWebsite.open_pdf(sous_bbox, largeur, hauteur),
              pdf_filename)
            open(pdf_filename + ".ok", 'a').close()
            time.sleep(ATTENTE_EN_SECONDE_ENTRE_DOWNLOAD)
        yield pdf_filename


def print_help():
    programme = sys.argv[0]
    spaces = " " * len(programme)
    sys.stdout.write((u"Téléchargement de PDF du cadastre" + "\n").encode("utf-8"))
    sys.stdout.write((u"USAGE:" + "\n").encode("utf-8"))
    sys.stdout.write((u"%s  DEPARTEMENT COMMUNE" % programme + "\n").encode("utf-8"))
    sys.stdout.write((u"           télécharge les export PDFs du cadastre d'une commune.\n").encode("utf-8"))
    sys.stdout.write((u"%s  " % programme + "\n").encode("utf-8"))
    sys.stdout.write((u"           liste les départements" + "\n").encode("utf-8"))
    sys.stdout.write((u"%s  DEPARTEMENT" % programme + "\n").encode("utf-8"))
    sys.stdout.write((u"           liste les communes d'un département" + "\n").encode("utf-8"))

def command_line_error(message, help=False):
    sys.stdout.write(("ERREUR: " + message + "\n").encode("utf-8"))
    if help: print_help()


def cadastre_vers_pdfs(argv):
  if len(argv) <= 1: 
      command_line_open_cadastre(argv)
  elif argv[1] in ["-h", "-help","--help"]:
      print_help()
  elif argv[1].startswith("-"):
      command_line_error(u"paramètres invalides")
  elif len(argv) == 2: 
      error = command_line_open_cadastre(argv)
      if error: command_line_error(error)
  elif len(argv) > 3: 
      command_line_error(u"trop d'arguments")
  else:
      cadastreWebsite = command_line_open_cadastre(argv)
      if type(cadastreWebsite) in [str, unicode]:
        command_line_error(cadastreWebsite, help=False)
      else:
        code_departement = cadastreWebsite.code_departement
        code_commune = cadastreWebsite.code_commune
        nom_commune = cadastreWebsite.communes[code_commune] 
        sys.stdout.write((u"Teléchargement des PDFs de la commune " + code_commune + " : " + nom_commune + "\n").encode("utf-8"))
        sys.stdout.flush()
        write_string_to_file("", code_commune + "-" + nom_commune + ".txt")
        return list(iter_download_pdfs(cadastreWebsite, code_departement, code_commune))

if __name__ == '__main__':
    list(cadastre_vers_pdfs(sys.argv))

