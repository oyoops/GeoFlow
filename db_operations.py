from utilities import CHUNK_SIZE
from shapefile_operations import make_multipolygon_if_not
from shapely.ops import transform
import logging
import psycopg2
import os


def establish_connection():
    """
    Establish a connection to the database and return the connection object.
    """
    print(f"  >> Connecting to the database...")
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER', "'postgres'"),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )
    print(f"  >> Successfully connected.")
    logging.info("Database connection established successfully.")
    return conn

def close_connection(conn):
    """
    Close the provided database connection.
    """
    print("Closing database connection...")
    conn.close()
    print(f"    ** Successfully closed connection! **")
    logging.info("Database connection closed successfully.")

def create_table_if_not_exists(conn, cleaned_county):
    try:
        with conn.cursor() as cur:
            cur.execute(f""" 
            SELECT EXISTS (
               SELECT FROM information_schema.tables 
               WHERE  table_schema = os.environ.get('DB_SCHEMA', "'public'")
               AND    table_name   = os.environ.get('DB_TABLE_NAME_FORMAT', "'parcels_{cleaned_county}'")
           );
            """)
            exists = cur.fetchone()[0]
            if not exists:
                cur.execute(f"""
                CREATE TABLE public.parcels_{cleaned_county} (
                    gid SERIAL PRIMARY KEY,
                    parcelno VARCHAR(255),
                    geom GEOMETRY(MultiPolygon, 4326)
                );
                """)
                conn.commit()
                print("  >> Successfully created a brand-new table.")
                logging.info("Table created successfully.")
    except Exception as e:
        logging.error(f"Error occurred during table creation. Error: {e}")
        print(f"Error occurred during table creation. Error: {e}")

def truncate_table(conn, cleaned_county):
    try:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE public.parcels_{cleaned_county};")
        conn.commit()
        print("  >> Successfully emptied the table.")
        logging.info("Table truncated successfully.")
    except Exception as e:
        logging.error(f"Error occurred during table truncation. Error: {e}")
        print(f"Error occurred during table truncation. Error: {e}")

def insert_data_into_db(gdf, conn, cleaned_county, start_index):
    # Set the CRS and then transform from EPSG:2236 (Florida East, NAD83) to EPSG:4326 (WGS84)
    gdf.crs = "EPSG:2236"
    gdf = gdf.to_crs("EPSG:4326")

    # Convert any 3D geometries to 2D (this fixes Palm Beach, maybe others)
    gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform(lambda x, y, z=None: (x, y), geom))

    try:
        # Validate geometries and log if invalid
        invalid_geoms = gdf[~gdf['geometry'].is_valid]
        if not invalid_geoms.empty:
            for idx, invalid in invalid_geoms.iterrows():
                logging.warning(f"Invalid geometry found at overall index {start_index + idx}.")
                print(f"       *  Invalid geometry found at #{start_index + idx}.")
        
        # Filter out invalid geometries before insertion
        gdf = gdf[gdf['geometry'].is_valid].copy()

        # Convert to MultiPolygon if not already
        gdf['geometry'] = gdf['geometry'].apply(make_multipolygon_if_not)

        with conn.cursor() as cur:
            data_tuples = [(row[os.environ.get('PARCEL_COLUMN_NAME')], row['geometry'].wkt) for _, row in gdf.iterrows()]
            # Using ST_GeomFromText directly within the query
            cur.executemany(f"""
            INSERT INTO public.parcels_{cleaned_county} (gid, parcelno, geom) 
            VALUES (DEFAULT, %s, ST_GeomFromText(%s, 4326));
            """, data_tuples)
        conn.commit()
        logging.info("Data insertion into the database completed successfully.")
    except Exception as e:
        logging.error(f"Error occurred during insertion for chunk starting at index {start_index}. Error: {e}")
        print(f"Error occurred during insertion for chunk starting at index {start_index}. Error: {e}")
