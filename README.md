# SafeWayHome

Our app SafeWayHome helps people which are scared when walking home by night feeling more safe by finding the safest route based on several criteria.
Based on the combination of a safety perception score and actual crime rates a creepiness score is calculated. According to this score, the app displays the safest route to the given destination. The fasted route is also provided.

## Data Acquisition
1) scrape criminal incidents from presseportal.de to gain a factual crime score, 
categorize incidents using a subsample trained on GPT3, 
finetuned on GPT2 (train on data from Frankfurt a.M., scalable for other cities)

2) scrape street view images from google maps, 
set up survey to determine safety perception and calculate a safety perception score

3) retrieve parks and industrial areas from OSM

## Calculation of Creepiness Score
For the Creepiness Score we combine the factual crime score and the safety perception score. According to the literature, while safety perception plays an important role for people actually feeling safe on a certain route, the perception does not always match actual crime rates. 
For more information on recent literature see LiteratureOverview.pdf
This is why in our app the factual crime rate score gets weighted with 2/3 and the perception score with 1/3. 
Additionally, parks and industrial areas get punished by an added point on the creepiness scale of 1 to 22.

## Interface
Our interface is based on a flask app. When entering the app, the users location is retrieved automatically. Once the user puts in their desired location the safest and fastest route are displayed to choose from. Especially unsafe areas are shaded red. Information on the length of the route and estimated time to arrival are displayed below the map.
For an enhanced user experience in a second tab the user can manipulate the crime-to-perception ratio as well as turn off the punishment for parks and industrial areas.

## Possible Extensions
There are various extensions that were out of the scope of this project but would be interesting:
- scaling up the app to other cities
- running more surveys to increase the baseline sample of the perception score
- including a feedback loop ('Did you feel safe here?')
- further research on the combination of perception and factual scores

