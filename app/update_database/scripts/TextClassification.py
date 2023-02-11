
import re
import requests
from geopy.geocoders import Nominatim
from datetime import datetime


CHECKPOINT = "pdg/gpt2_ft_police_articles"
BASE_URL = "https://api-inference.huggingface.co/models/"
API_URL = BASE_URL + CHECKPOINT

TOKEN = "Bearer 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"
headers = {"Authorization": TOKEN}


RELEVANT_CRIMES = ["Tötungsdelikt", "Sexualdelikt", "Raub", "Körperverletzung", "Drogendelikt", "Diebstahl"]


def model_query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response


def extract_crime_data(article):

    TASK = "Extract the crime, the location and whether the crime happend indoors \n"
    INPUT_TEXT = "TEXT: " + article[:1000] + "\n"
    CRIME = "CRIME: "

    prompt = TASK + INPUT_TEXT + CRIME

    output = model_query({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 25,
                       "num_beams": 5,
                       "temperature": 0.6,
                       },
        "options": {"wait_for_model": True,
                    "use_cache": True}
    })

    crimes, location, indoors = [None] * 3
    print(output.text)

    m = re.search(r'CRIME: (.*?)\\n', output.text)
    if m:
        print(m.groups()[0])
        crimes = [c for c in m.groups()[0].strip().split(", ") if c in RELEVANT_CRIMES]

    m = re.search(r'LOC: (.*?)\\n', output.text)
    if m:
        location = m.groups()[0].strip()

    m = re.search(r'INDOORS: (.*?)\\n', output.text)
    if m:
        indoors = m.groups()[0].strip()

    if not str(location) in article:
        location = None

    return crimes, location, indoors


def get_lat_lon(country, city, street):
    # get coordinates of streets
    try:
        geolocator = Nominatim(user_agent="tutorial")
        location = geolocator.geocode(", ".join([country, city, street]), timeout=3).raw
    except:
        return None, None

    return location["lat"], location["lon"]


def article_to_crime_data(article):

    crimes, street, indoors = extract_crime_data(article["headline"] + "\n" + article["article"])
    print(crimes, street, indoors)
    if crimes and street and not indoors:
        lat, long = get_lat_lon(article["country"], article["city"], street)
        if lat and long:
            c = {"country": article["country"],
                 "city": article["city"],
                 "street": street,
                 "lat": lat,
                 "long": long,
                 "tötungsdelikt": ("Tötungsdelikt" in crimes),
                 "sexualdelikt": ("Sexualdelikt" in crimes),
                 "körperverletzung": ("Körperverletzung" in crimes),
                 "raub": ("Raub" in crimes),
                 "diebstahl": ("Diebstahl" in crimes),
                 "drogendelikt": ("Drogendelikt" in crimes)}
            return c
    else:
        return None
