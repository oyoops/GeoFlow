
# GeoFlow

*This entire description was written by ChatGPT.*  
*I don't have the time.*  
*Code by @oyoops*

## Shapefile Streamer & Visualizer

*GeoFlow* seamlessly bridges the gap between vast shapefile datasets and PostgreSQL databases, empowering users with the ability to visualize, transform, and manage geospatial data with unparalleled ease.

## 🚀 Highlights

- **Chunked Processing**: Efficiently handle colossal shapefiles without memory hiccups.
- **GeoJSON Streaming**: Directly stream your geospatial data to the universal GeoJSON format.
- **Interactive Mapping**: Visualize your datasets on-the-fly with elegant, interactive maps.
- **Database Flexibility**: Designed for PostgreSQL with PostGIS, ensuring robust geospatial capabilities.

## 📚 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Dive In: Usage](#dive-in-usage)
4. [Behind The Scenes: Module Insights](#behind-the-scenes-module-insights)
5. [Join the Flow: Contributing](#join-the-flow-contributing)
6. [License & Credits](#license--credits)

## 🛠 Prerequisites

- **Python Landscape**: Python 3.x environment.
- **Python Libraries**: `fiona`, `geopandas`, `psycopg2`, `shapely`, `folium`, `itertools`, `psutil`.
- **Database Realm**: PostgreSQL equipped with the PostGIS extension.

## 📦 Installation & Setup

```bash
# Clone the heart of GeoFlow
git clone <repository_url>

# Step into the world of GeoFlow
cd GeoFlow

# Prepare your toolkit
pip install -r requirements.txt
```

## 🌊 Dive In: Usage

1. Awaken GeoFlow:
```bash
python main.py
```
2. Let GeoFlow guide you. Input the desired county name and watch the magic unfold.

## 🧩 Behind The Scenes: Module Insights

1. **main.py**: 
    - The command center. Orchestrates the symphony of reading, processing, and storing geospatial wonder.

2. **db_operations.py**: 
    - The database maestro. Connect, create, curate.

3. **shapefile_operations.py**: 
    - The shapefile sage. Reads, processes, and delivers geospatial intelligence.

4. **geojson_operations.py**: 
    - The GeoJSON guru. Streams, visualizes, and celebrates geospatial data.

5. **utilities.py**: 
    - The unsung hero. Monitors, logs, and supports.

## 🌌 Join the Flow: Contributing

Every droplet makes an ocean. Your contributions can enhance the flow of GeoFlow. Dive in with a pull request or ripple an issue to discuss improvements.

## 📄 License & Credits

Sculpted with ❤️ by @oyoops. Description by ChatGPT. Licensed under [MIT License](LICENSE).
