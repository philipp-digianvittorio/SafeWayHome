import geopandas as gpd
import osmnx as ox 
import matplotlib.pyplot as plt

city = "Frankfurt"
gdf = ox.geocode_to_gdf(city) # get boundaries of FFM

# 0) Get polygons of districts

districts = ox.geometries.geometries_from_place(city, {'place':'suburb'})

for i in range(len(districts)):
    gdf = ox.geocode_to_gdf(districts['name'][i] + "," + city)
    gdf['name'] = districts['name'][i] # add district name as separate element
    if i == 0:
        district_polygons = gdf
    else:
        district_polygons = pd.concat([district_polygons, gdf])
district_polygons.to_file("districts.json")

# 1) Parks
parks = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'leisure': 'park'})
parks_save = parks.applymap(lambda x: str(x) if isinstance(x, list) else x)
parks_final = gpd.clip(parks_save, gdf)
parks_final.to_file("parks.json")

# plot parks
fig, ax = plt.subplots(figsize = (8,8))
parks_final.plot(ax = ax, color = '#97c1a9', edgecolor = 'black',)
plt.title('All parks in FFM')
plt.show()

# 2) Industral areas
industrial = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'landuse': 'industrial'})
industrial_save = industrial.applymap(lambda x: str(x) if isinstance(x, list) else x)
industrial_final = gpd.clip(industrial_save, gdf)
industrial_final.to_file("industrial.json")

# plot industrial areas
fig, ax = plt.subplots(figsize = (8,8))
industrial_final.plot(ax = ax, color = '#bbbbbb', edgecolor = 'black',)
plt.title('All industrial areas in FFM')
plt.show()