import logging
import geopandas as gpd
import folium
import json
import os


# Function for saving data to geojson (this streams directly from db -> GeoJSON)
def stream_geojson_to_file(conn, table_name, output_path, chunk_size=10000):
    print("\nStreaming from the database to a new GeoJSON...")
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_records = cur.fetchone()[0]

    with open(output_path, 'w') as file:
        file.write('{"type": "FeatureCollection", "features": [')

        for offset in range(0, total_records, chunk_size):
            sql = f"""
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', gid,
                'geometry', ST_AsGeoJSON(geom)::jsonb,
                'properties', to_jsonb(row) - 'gid' - 'geom'
            )
            FROM (SELECT * FROM {table_name} LIMIT {chunk_size} OFFSET {offset}) AS row;
            """
            with conn.cursor() as cur:
                cur.execute(sql)
                records = cur.fetchall()
                chunk_str = ",".join([json.dumps(rec[0]) for rec in records])
                file.write(chunk_str)
                if offset + chunk_size < total_records:
                    file.write(",")

        file.write("]}")
        print(f"    ** Successfully streamed to GeoJSON! **")
        logging.info(f"Data streamed to GeoJSON successfully.")

# Function to save the data as KML
# (NOT YET IMPLEMENTED)

# Function for generating an HTML map from a GeoJSON
def generate_html_map(geojson_path, county_name):
    """
    Generate an HTML map with 50 plotted parcels.

    Parameters:
    - geojson_path: Path to the GeoJSON file.
    - county_name: Name of the county.
    """

    # Load the entire GeoJSON file into memory (there has got to be a more efficient way to do this...)
    print("\nLoading the new GeoJSON into memory...")
    geo_df = gpd.read_file(geojson_path)
    print(f"    ** Successfully loaded GeoJSON! **\n")
    
    # Generate the HTML map
    print(f"\nGenerating an interactive parcel map from the {county_name} GeoJSON...")
    
    # Select first 50 parcels
    selected_df = geo_df.head(50)

    # Create a folium map centered on the first parcel
    center = selected_df.iloc[0].geometry.centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=13)

    # Add the selected data to the map
    folium.GeoJson(selected_df).add_to(m)

    # Save the map as an HTML file
    output_html_path = os.environ.get('HTML_MAP_PATH_FORMAT')
    m.save(output_html_path)
    print(f"    ** Successfully generated HTML map! **")
    print(f"       - Public Location:  {os.environ.get('MAPS_DOMAIN_NAME')}/counties/{county_name}.html")
    print(f"       - Server Location:  {output_html_path}\n")
