import ee
import datetime
import webbrowser
import geemap

# FIRST TIME ONLY: Uncomment this line to authenticate
#ee.Authenticate()

# Initialize Earth Engine
ee.Initialize(project='inspiring-modem-462205-v7')

# Define the area of interest - Umzimvubu Catchment near Matatiele, [xmin, ymin, xmax, ymax]
geometry = ee.Geometry.Rectangle([28.3, -31.3, 30.5, -30.0])

# Load MODIS NDVI data (MOD13Q1 - 16 day composite)
ndvi_dataset = ee.ImageCollection('MODIS/006/MOD13Q1') \
    .filterDate('2013-01-01', '2023-12-31') \
    .filterBounds(geometry) \
    .select('NDVI')

# Print the number of NDVI images loaded
count = ndvi_dataset.size().getInfo()
print(f"Loaded {count} NDVI images.")

# Calculate yearly median NDVI
def get_yearly_ndvi(year):
    start = ee.Date.fromYMD(year, 1, 1)
    end = start.advance(1, 'year')
    ndvi_year = ndvi_dataset.filterDate(start, end).median().clip(geometry)
    return ndvi_year.set('year', year)

# Create a collection of yearly NDVI images
years = list(range(2013, 2024))
ndvi_by_year = ee.ImageCollection([get_yearly_ndvi(y) for y in years])

# Select the NDVI image for 2023
image_2023 = ndvi_by_year.filter(ee.Filter.eq('year', 2023)).first()

# Export the NDVI 2023 image to Google Drive
task = ee.batch.Export.image.toDrive(
    image=image_2023,
    description='NDVI_2023_Umzimvubu',
    folder='EarthEngine',
    fileNamePrefix='NDVI_2023',
    region=geometry,
    scale=250,
    maxPixels=1e13
)

task.start()
print("Export started... Check Google Drive in a few minutes.")

# Create a map centered near Matatiele
Map = geemap.Map(center=[-30.6, 29.5], zoom=8)

# Add the NDVI 2023 image to the map with visualization parameters
vis_params = {
    'min': 0,
    'max': 9000,
    'palette': ['white', 'yellow', 'green']
}
# Create an interactive map centered on the area
Map = geemap.Map(center=[-30.6, 29.5], zoom=8)

#Add each yearly NDVI image to the map
for year in years:
    image = ndvi_by_year.filter(ee.Filter.eq('year', year)).first()
    Map.addLayer(image, vis_params, f'NDVI {year}')

#Legend
Map.add_Legend(title="NDVI", labels=["Low", "Medium", "High"], colors=["white", "yellow", "green"])

# Export interactive map as HTML and open in browser
Map.to_html('ndvi_all_years_map.html')
webbrowser.open('ndvi_all_years_map.html')
