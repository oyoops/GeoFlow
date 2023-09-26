import os
import logging
import fiona
import itertools
import geopandas as gpd
from shapely.geometry import MultiPolygon, shape
from utilities import CHUNK_SIZE


def count_features_in_shapefiles(shapefiles):
    total_features = 0
    for shapefile in shapefiles:
        with fiona.open(shapefile) as src:
            total_features += len(src)
    print(f'\nFound {total_features} parcels for insertion.')
    return total_features


def calculate_total_chunks(shapefile, chunk_size=CHUNK_SIZE):
    with fiona.open(shapefile) as src:
        total = len(src)
        return -(-total // chunk_size)


def read_shapefile_in_chunks(shapefile, chunk_size=CHUNK_SIZE):
    with fiona.open(shapefile) as src:
        total = len(src)
        for i in range(0, total, chunk_size):
            records = list(itertools.islice(src, chunk_size))
            if not records:
                break
            data = {
                os.environ.get('PARCEL_COLUMN_NAME', "'PARCELNO'"): [rec['properties'][os.environ.get('PARCEL_COLUMN_NAME', "'PARCELNO'")] for rec in records],
                'geometry': [shape(rec['geometry']) for rec in records]
            }
            yield gpd.GeoDataFrame(data, geometry='geometry')


def make_multipolygon_if_not(geom):
    if geom.geom_type == 'Polygon':
        return MultiPolygon([geom])
    return geom

