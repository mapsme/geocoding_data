#!/usr/bin/env python3
import psycopg2
import json


DB_NODE_BASE = 50*1000*1000*1000


class OsmIdCode:
    NODE = 0x4000000000000000
    WAY = 0x8000000000000000
    RELATION = 0xC000000000000000
    RESET = ~(NODE | WAY | RELATION)


def osmid_to_rid(osm_id):
    if osm_id < 0:
        rid = (-osm_id) | OsmIdCode.RELATION
    elif osm_id > DB_NODE_BASE:
        rid = (osm_id - DB_NODE_BASE) | OsmIdCode.NODE
    else:
        rid = osm_id | OsmIdCode.WAY
    if rid >= 2**63:
        # Negate as in int64_t
        rid = -1 - (rid ^ (2**64 - 1))
    return rid


if __name__ == '__main__':
    cursor = psycopg2.connect('dbname=borders').cursor()
    cursor.execute('''select osm_id, level, name,
                   coalesce(tags->'name:en', tags->'int_name', tags->'name:es'),
                   rank, ST_X(centroid), ST_Y(centroid)
                   from osm_polygon where rank <= 14 and name is not null order by rank limit 1000''')

    for region in cursor.fetchall():
        osm_id, level, name, int_name, rank, lon, lat = region
        cursor.execute('''select level, osm_id, name,
                       coalesce(tags->'name:en', tags->'int_name', tags->'name:es')
                       from osm_polygon p join osm_polygon_geom g using (osm_id)
                       where ST_Intersects(g.way, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                       and rank < %s''', (lon, lat, rank))
        addr = {level: name}
        addr_en = {level: int_name}
        for row in cursor:
            addr[row[0]] = row[2]
            addr_en[row[0]] = row[3]
            addr[row[0]+'_id'] = osmid_to_rid(row[1])
            addr_en[row[0]+'_id'] = osmid_to_rid(row[1])
        feature = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {'name': name, 'rank': rank, 'address': addr, 'address_en': addr_en}
        }
        print(str(osmid_to_rid(osm_id)) + ' ' + json.dumps(feature, ensure_ascii=False))
