import overpy


def get_police_coords(latitude, longitude):
    # Initialize the API
    api = overpy.Overpass()

    # Define the query
    query = """(node["amenity"="police"](around:2000,{lat},{lon});
            );out;
            """.format(lat=latitude, lon=longitude)
    # Call the API
    result = api.query(query)
    return result
    
#Freiburg 47.997791, 7.842609

