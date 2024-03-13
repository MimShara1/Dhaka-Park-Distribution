
"""""
Analysis of Dhaka city park distribution among its Thanas' (Thana:smaller administrative unit of city in Bangladesh).
The objective of this analysis to identify the geographical distribution of parks within Thanas of Dhaka city.
Author: Sharmin Shara Mim
Last Updated: 05.03.2024

Querying the OSM park data within an AOI and exports it as Geopackage. Computing the park ratio for Thanas and exports
it as Shapefile. Merging two datasets Thanas and district park ratio for mapping and visualizing. 
"""""
#Defining required libraries
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import osmnx as ox
import pandas as pd
import contextily as cx

# Load Working Directory
os.getcwd()
os.chdir('C:\\Users\\raiya\\Downloads\\Python Project')


### PART I: Retrieve OSM Park Data
#Constructing the Path of Data
path_AOI = os.path.join(os.getcwd(),"dhaka.shp")
type(path_AOI)
#Constructing the Path to Store the Data
path_osm_data = os.path.join(os.getcwd(),"OSM parks")
#Read Data
aoi_gdf = gpd.read_file(path_AOI)
print(aoi_gdf.crs) #Checking the CRS of data. Here,the library requires EPSG 4326 and this dataset CRS is already EPSG 4326.

#Accessing the OSM Park data through osmnx package:
parks_aoi = ox.features_from_polygon(aoi_gdf.geometry[0], tags={'leisure': 'park'})
parks_aoi = parks_aoi[parks_aoi.index.get_level_values('element_type') == 'way'].geometry


#Export Data as Geopackage
parks_aoi.to_file(path_osm_data +'parks_aoi.gpkg')


###PART II: Computing the Park Ratio
#Read our recently stored parks_aoi data
park_gdf = gpd.read_file(r'C:\Users\raiya\Downloads\Python Project\parks_aoi.gpkg')
print(park_gdf.columns) #To check the available columns in dataset
park_gdf_3857 = park_gdf.to_crs(epsg=3857) #Converting CRS EPSG:4326 to EPSG:3857
print(park_gdf_3857.crs) #To be sure CRS has been converted
#Read Data dhaka_thanas
dhaka_gdf = gpd.read_file(r'C:\Users\raiya\Downloads\Python Project\dhaka_thanas.gpkg')
print(dhaka_gdf.crs) #To check the dataset CRS
dhaka_gdf_3857 = dhaka_gdf.to_crs(epsg=3857) #Again converting CRS from EPSG:4326 to EPSG:3857 to make sure both datasets are in same CRS.
print(dhaka_gdf_3857.crs) #To check the conversion of CRS


#We create a new Geodataframe with the Dhaka Thanas' geometries and populate it with the computed park ratio.
#We also create a new column park_ratio for this attribute
new_district_gdf = gpd.GeoDataFrame(data={'park_ratio':[]}, geometry=gpd.GeoSeries(dhaka_gdf_3857.geometry))

#We have to work with full Geodataframe here, not only one Geodataframe since we would store the computed value inside of the  new Geodataframe
for district_idx in new_district_gdf.index:
    print(district_idx) #To check the dataset what is inside

#Here we access the specific district of our dataset using the .iloc[] method
    district = new_district_gdf.iloc[district_idx]
    district_geom = district.geometry #And we access the specific district footprint by taking its geometry
    sample_park = park_gdf_3857.clip(mask=district.geometry) #Performing clip to create a new park area which falls within the specific district geometry
    local_park_ratio = sample_park.area.sum()/district.geometry.area #Computing the local park ratio
    print(local_park_ratio)
    new_district_gdf.loc[district_idx, 'park_ratio'] = local_park_ratio #Here we restore the value of the local park density  around the district into the row of that district in the column of the new attribute
#Export the computed park ratio in Shapefile
new_district_gdf.to_file('..\\district_park_ratio.shp')

### PART III: Performing Spatial Join and Data Visualization

#Read the recently constructed Shapefile district_park_ratio and store it in a new Geodataframe named 'distribution'
distribution_gdf = gpd.read_file(r'C:\Users\raiya\Downloads\Python Project\district_park_ratio.shp')

#Now we perform a spatial join to merge the attributes of newly created distribution Geodataframe with existing Geodataframe 'dhaka_gdf_3857
spatial_join = gpd.sjoin(dhaka_gdf_3857,distribution_gdf, how="inner", predicate="within")
spatial_join.head() #To be sure what attributes there are

# Here we are aggregating the geometries of Thanas' with park ratio using groupby function
grouped_park_area = spatial_join.groupby('THANA_NAME')['park_ratio'].sum().reset_index()
print(grouped_park_area)

# We are merging two datasets 'grouped_park_area' and 'dhaka_gdf_3857' using 'THANA_NAME' columns
district_park_ratio = dhaka_gdf_3857.merge(grouped_park_area, on='THANA_NAME', how='left')

#Visualize the Dhaka park ratio Thana wise
ax = district_park_ratio.plot(figsize=(8, 6),
             column="park_ratio",
             cmap="Greens",
             legend="park_ratio",
             linewidth=1,
             edgecolor="black"
             )

# Add a basemap using contextily (cx)
cx.add_basemap(ax, crs=district_park_ratio.crs.to_string(), source=cx.providers.CartoDB.DarkMatterNoLabels)
cx.add_basemap(ax, crs=district_park_ratio.crs.to_string(), source=cx.providers.CartoDB.DarkMatterOnlyLabels)
#Set labels and title
ax.set_title('Park Distribution of Dhaka Thana-wise')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Save the map to an image  file
plt.savefig('dhaka_park ratio_map.jpg', dpi=300, format='jpg')


###PART IV: Data Visualization with appropriate plots
#Sort the park_ratio column in descending order
district_park_ratio=district_park_ratio.sort_values(by='park_ratio', ascending=False)
# We create a bar diagram to visualize Thana wise park ratio
fig, ax = plt.subplots(figsize=(10, 10))
district_park_ratio.plot.bar(x='THANA_NAME', y='park_ratio', color='blue', ax=ax)
print(district_park_ratio.columns)
ax.set_xlabel('Thanas')
ax.set_ylabel('Park Ratio')
ax.set_title('Park Ratio in Dhaka City Thanas')
plt.show()

#Save the bar plot in an image
plt.savefig('bar diagram dhaka park ratio.jpg', dpi=300, format='jpg')


#Now we create a pie chart to show the park distribution among Thanas' in percentage
#Create a dictionary list containing Thana names and park ratio data
park_ratio_data = {
    'THANA': ['Dhaka Metro', 'Nawabganj', 'Dohar','Dhamrai','Savar','Keraniganj'],
    'Park_Ratio':[8.0114e-03,1.7626e-04,6.0754e-04,4.1221e-05,1.3571e-03,3.3594e-04]
}

park_ratio_df = pd.DataFrame(park_ratio_data) # Create a dataframe using panda library

# Plotting
fig, ax = plt.subplots()

# Plot the pie chart based on auto percentage format
ax.pie(park_ratio_df['Park_Ratio'], labels=park_ratio_df['THANA'], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)

# Set title
ax.set_title('Park Ratio for Dhaka city  Thana wise')

# Visualize the plot
plt.show()

#Save the pie plot in an image
plt.savefig('pie diagram dhaka park ratio.jpg', dpi=300, format='jpg')

###PART V: Calculting Population Density for Dhaka city Thanas' and visualizing it with choropleth map

#Create a dictionary list containing Thana and Population data
population_data = {
    'THANA': ["Dhaka Metro","Nawabganj (Dhaka)", "Dhamrai", "Dohar", "Savar", "Keraniganj"],
    'Population': [8906039,318811,412418,226439,1385910,794360, ]
}

population_df = pd.DataFrame(population_data) #create a population dataframe using panda library
population_df.head() #To be sure the contents of dataframe

dhaka_thanas_list = ['Dhaka Metro', 'Dhamrai', 'Dohar','Keraniganj','Nawabganj (Dhaka)','Savar'] #Create a seperate list of Thanas'

# Read 'dhaka_thanas' Geopackage and store it in a new Geodataframe named 'gdf_thanas'
gdf_thanas = gpd.read_file(r"C:\Users\raiya\Downloads\Python Project\dhaka_thanas.gpkg")
gdf_thanas_3857 = gdf_thanas.to_crs(epsg=3857)

#Here we merge the Population dataframe with Dhaka Thanas' Geodataframe based on 'THANA_NAME'column
merged_gdf = gdf_thanas_3857.merge(population_df, how='left', left_on='THANA_NAME', right_on='THANA')

# And we filter 'merged_gdf'Geodataframe based on 'THANA_NAME' column and Dhaka Thanas' list and store it in a new geodataframe named 'dhaka_thana_gdf'
dhaka_thana_gdf = merged_gdf[merged_gdf['THANA_NAME'].isin(dhaka_thanas_list)]

# We convert the Thanas' area from Square meters to square kilometers and calculates population density Thana-wise
population_density_gdf = dhaka_thana_gdf['Population'] / (dhaka_thana_gdf['geometry'].area/1000000)

# Add Population Density to the Dhaka Thana Geodataframe
dhaka_thana_gdf['Population_Density'] = population_density_gdf

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Plot the choropleth map of Population Density Thana wise
dhaka_thana_gdf.plot(column='Population_Density', cmap='viridis_r', linewidth=1, ax=ax, edgecolor='g', legend=True)
# Add a basemap using contextily (cx)
cx.add_basemap(ax, crs=dhaka_thana_gdf.crs.to_string(), source=cx.providers.CartoDB.DarkMatterNoLabels)
cx.add_basemap(ax, crs=dhaka_thana_gdf.crs.to_string(), source=cx.providers.CartoDB.DarkMatterOnlyLabels)

# Set labels and title
ax.set_title('Population Density in Dhaka Thana-wise')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
# Save the map to an image  file
plt.savefig('dhaka_population density_map.jpg', dpi=300, format='jpg')
# Visualize the plot
plt.show()

