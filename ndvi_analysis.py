#Import required modules to bring Earth Engine Python API
import ee
#Import datetime: Helps with working with dates when need custom date ranges later
import datetime

# Initialize Earth Engine - authenticates and connects script to Earth Engine account
ee.Initialize()

# Define the area of interest - Umzimvubu Catchment near Matatiele, [xmin, ymin, xmax, ymax]
geometry = ee.Geometry.Rectangle([28.3, -31.3, 30.5 -30.0])

# Load MODIS NDVI data (MOD13Q1-16 day composite)
ndvi_dataset = ee.ImageCollection('MODIS/006/MOD13Q1') \
    .filterDate('2013-01-01', '2023-12-31') \
    .filterBounds(geometry) \
    .select('NDVI')

#Print the number of NDVI images loaded
count = ndvi_dataset.size().getInfo()
print(f"Loaded {count} NDVI images.")

#Calculate yearly median NDVI
def get_yearly_ndvi(year):
    start = ee.Date.fromYMD(year, 1, 1)
    end = start.advance(1,'year')
    ndvi_year = ndvi_dataset.filterDate(start, end).median().clip(geometry)
    return ndvi_year.set('year', year)

years=list(range(2013, 2024))
ndvi_by_year = ee.ImageCollection([get_yearly_ndvi(y) for y in years])


# Select the NDVI image for 2023 
image_2023 = ndvi_by_year.filter(ee.Filter.eq('year', 2023)).first()

#Export that image to Google Drive
task = ee.batch.Export.image.toDrive(
    image=image_2023,
    description='NDVI_2023_Umzimvubu',
    folder='EarthEngine',
    fileNamePrefix='NDVI_20230',
    region=geometry,
    scale=250,
    maxPixels=1e13
)

task.start()
print("Export started... Check Google Drive in a few minutes.")

