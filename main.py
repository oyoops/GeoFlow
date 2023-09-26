from shapefile_operations import count_features_in_shapefiles, read_shapefile_in_chunks, calculate_total_chunks
from geojson_operations import stream_geojson_to_file, generate_html_map
from db_operations import (create_table_if_not_exists, truncate_table, insert_data_into_db, establish_connection, close_connection)
from utilities import CHUNK_SIZE
import logging
import sys
import gc
import os


# Check that county argument was provided
if len(sys.argv) < 2:
    print("Usage: python main.py <county_name>")
    sys.exit(1)
county_input = sys.argv[1]
cleaned_county = county_input.lower().replace("county", "").replace(" ", "").replace("-", "").replace(".", "").replace("'", "")
shapefiles = [os.environ.get('SHAPEFILE_PATH_FORMAT', "'{cleaned_county}_2023pin/{cleaned_county}_2023pin.shp'")]

# Connect to sb102bot_db (PostgreSQL database w/ PostGIS)
conn = establish_connection()

# Ensure this county's table exists; create it if it doesn't
create_table_if_not_exists(conn, cleaned_county)

# Empty all contents from the table, if any exist
truncate_table(conn, cleaned_county)

# Calculate total features to be added across all shapefiles
total_features = count_features_in_shapefiles(shapefiles)

# Insert the data into the database in chunks
for idx, shapefile in enumerate(shapefiles, 1):
    total_chunks = calculate_total_chunks(shapefile, CHUNK_SIZE)
    print(f"\n  [SHAPEFILE #{idx}]")
    for chunk_index, chunk_gdf in enumerate(read_shapefile_in_chunks(shapefile, CHUNK_SIZE), 1):
        try:
            start_index = (chunk_index - 1) * CHUNK_SIZE
            print(f"     Processing chunk {chunk_index} of {total_chunks}...")
            insert_data_into_db(chunk_gdf, conn, cleaned_county, start_index)
            logging.info(f"Processed chunk {chunk_index} out of {total_chunks} from shapefile #{idx}")
        except Exception as e:
            print(f"  Error processing chunk {chunk_index} out of {total_chunks} from {shapefile}. Error: {e}")
            logging.error(f"Error processing chunk {chunk_index} out of {total_chunks} from {shapefile}. Error: {e}")
        # Delete the GeoDataFrame to free up memory
        del chunk_gdf
        gc.collect()
logging.info("All database insertions finished.")
print(f'\nRemember, the total number of features across all shapefiles was {total_features}.\nYou should verify that {total_features} matches the number of rows that were actually inserted into the table.')
print(f"\n     :-D       :-D\n      .-------.\n :-D  | DONE! |    :-D\n      '-------'       :-D\n   :-D          :-D")

# Stream the table from db to a GeoJSON file
geojson_output_path = f"{cleaned_county}_2023pin/{cleaned_county}.geojson"
stream_geojson_to_file(conn, f"public.parcels_{cleaned_county}", geojson_output_path)

# Generate the HTML map
generate_html_map(geojson_output_path, cleaned_county)

# # Save the data as KML
# (NOT YET IMPLEMENTED)

# Close the database connection
close_connection(conn)

# Done
print(f"\n\nFINISHED! :-D\n")