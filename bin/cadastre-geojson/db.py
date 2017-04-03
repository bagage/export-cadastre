#!/usr/bin/env python

import sys
import os.path
import psycopg2

dbstring = file(os.path.join(os.path.dirname(sys.argv[0]), ".database-connection-string")).read()
db = psycopg2.connect(dbstring)
#db.autocommit = True
cur = db.cursor()


TABLE_PREFIX="cadastre_geojson_"

def execute(query, args = tuple()):
    print cur.mogrify(query, args)
    return cur.execute(query, args)

def fetchall():
    return cur.fetchall()
