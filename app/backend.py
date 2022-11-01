import overpy


def get_shops(latitude, longitude):
    # Initialize the API
    api = overpy.Overpass()

    # Define the query
    query = """(node["amenity"="bar"](around:500,{lat},{lon});
               node["amenity"="police"](around:500,{lat},{lon});
            );out;
            """.format(lat=latitude, lon=longitude)
    # Call the API
    result = api.query(query)
    return result
    
#Freiburg 47.997791, 7.842609

