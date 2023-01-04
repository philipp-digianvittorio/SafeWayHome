import openai
from app.db_update.scripts.PresseportalScraper import PresseportalScraper

sc = PresseportalScraper()
hq = sc.get_police_headquarters()
fra = [x for x in hq if "Polizeipräsidium Frankfurt" in x["name"]][0]
articles = sc.get_articles(fra, max_articles=50)

api_key = "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"

def GPT_Completion(api_key, prompt, max_tokens=256):
    openai.api_key = api_key
    response = openai.Completion.create(engine="text-davinci-003",
                                        prompt=prompt,
                                        temperature=0.6,
                                        top_p=1,
                                        max_tokens=max_tokens,
                                        frequency_penalty=0,
                                        presence_penalty=0)
    print(response.choices)
    return response.choices[0].text



task = "Ordne für jeden Vorfall die Straftat einer der folgenden Klassen zu - Betrug, Diebstahl, Hausfriedensbruch, Einbruch, Raub, schwerer Raub, Erpressung, Verkehrsunfall, Verkehrsstraftat, Drogenhandel, Drogenbesitz, Waffenbesitz, Sachbeschädigung, Brandstiftung, fahrlässige Körperverletzung, Körperverletzung, gefährliche Körperverletzung, schwere Körperverletzung, Bedrohung, Widerstand, Exhibitionismus, sexuelle Belästigung, sexueller Übergriff, Vergewaltigung, Beleidigung, Tötungsdelikt, Sonstiges. Benenne den Haupttatort (Straße) und den Beginn der Tatzeit (Uhrzeit) und gib an, ob die Straftat in einem Gebäude begangen wurde: "

ex1 = '''Text: (th) Am Dienstag (22.11.2022) wurden zwei Crackdealer nach beobachteten Verkäufen festgenommen.
Vormittags folgten zivile Polizeibeamte zwei Drogenkonsumenten vom Bahnhofsgebiet zum Schweizer Platz, wo sie auf ihren Dealer trafen und ca. 0,25 Gramm Crack in Empfang nahmen. Die beiden Käufer wurden vor Ort kontrolliert, der 42-jährige wohnsitzlose Dealer im Bereich Eschenheimer Tor festgenommen. Er führte weitere ca. 0,5 Gramm Crack bei sich, welche er versuchte zu schlucken. Ihm konnte ein weiterer Drogenhandel nachgewiesen werden, welcher einige Monate zurücklag. Es folgte die Einlieferung in das Zentrale Polizeigewahrsam zwecks Prüfung einer richterlichen Vorführung.
Gegen 18:00 Uhr wurden Polizeibeamte auf einen weiteren Dealer im Bereich Am Hauptbahnhof aufmerksam. Sie identifizierten ihn als Verkäufer aus einem wenige Tage zuvor beobachteten Drogenhandel. Er wurde festgenommen. Gegen den ebenfalls 42-Jährigen Wohnsitzlosen bestand zudem ein offener Haftbefehl.'''
result1 = '''[{'crime': ['Drogenhandel',], 'location': 'Schweizer Platz', 'time': 'Vormittag', 'indoors': False}, {'crime': ['Drogenhandel',], 'location': 'Am Hauptbahnhof', 'time': '18:00 Uhr', 'indoors': False}]'''

ex2 = '''Text: (dr) Eine Polizeistreife des 4. Reviers nahm am gestrigen Sonntag, den 20. November 2022, einen 19-Jährigen im Gutleutviertel fest, der sich bei einer Personenkontrolle besonders aggressiv zeigte. Bei ihm stellten sie auch Rauschgift sicher.
Eine Ruhestörung in der Gutleutstraße führte gegen 22:10 Uhr zu einer Personenkontrolle eines 19-Jährigen. Der junge Mann war offensichtlich nicht mit der polizeilichen Maßnahme einverstanden und machte dies deutlich, indem er Tritte und Schläge gegen die ihn kontrollierenden Beamten austeilte. Währenddessen versuchte er auch immer wieder ein Einhandmesser aus seiner Jackentasche zu ziehen, was jedoch unterbunden werden konnte. Den Beamten gelang es, den 19-Jährigen unter Widerstand festzunehmen. Als sie ihn durchsuchten, stießen sie auf Betäubungsmittel, darunter rund 90 Gramm Amphetamin und über 90 Ecstasy-Tabletten. Bei einer anschließenden Durchsuchung an der Anschrift seiner Eltern fanden die Beamten in seinem "Kinderzimmer" weitere Substanzen zur Herstellung von Drogen auf sowie verbotene Gegenstände. Sie stellten alle Beweismittel sicher.
Für den 19-Jährigen, welcher über keinen festen Wohnsitz verfügt, ging es in der Folge in die Haftzellen. Ihn erwartet nun ein Strafverfahren wegen des Verdachts des illegalen Drogenhandels und des Widerstands gegen Vollstreckungsbeamte. Er soll heute dem Haftrichter vorgeführt werden.'''
result2 = '''[{'crime': ['Sonstiges', 'Drogenhandel', 'Widerstand',], 'location': 'Gutleutstraße', 'time': '22:10 Uhr', 'indoors': False}]'''

ex3 = '''Text: (wie) Ein berauschter Autofahrer ohne Führerschein ist in der Nacht von Freitag auf Samstag bei Hattersheim vor der Polizei geflohen, konnte aber festgenommen werden.
Eine Streife der Autobahnpolizei wollte gegen 01:20 Uhr einen blauen Audi kontrollieren, da er mit eingeschalteter Nebelschlussleuchte auf der A 66 unterwegs war. Der Fahrer missachtete allerdings die Anhaltezeichen und wendete sein Fahrzeug, nachdem die Fahrzeuge bei Zeilsheim von der Autobahn abgefahren waren. Der Audi floh durch Zeilsheim und Sindlingen, überholte einen Linienbus mit hoher Geschwindigkeit und gefährdete in der Sindlinger Bahnstraße einen Fußgänger, der gerade einen Zebrastreifen nutzen wollte, aber rechtzeitig auf den Bürgersteig zurücktrat. Die Fahrt ging weiter bis nach Hattersheim, wo auch ein Fußgänger an einem Zebrastreifen gefährdet wurde. Schließlich konnte der Audi von Beamten der Autobahnpolizei und einem Frankfurter Streifenwagen gestoppt und der Fahrer festgenommen werden. Der 18-Jährige aus Straßburg stand offensichtlich unter dem Einfluss von Betäubungsmitteln und war nicht im Besitz einer Fahrerlaubnis.
'''
result3 = '''[{'crime': ['Verkehrsstraftat',], 'location': 'Hattersheim', 'time': '01:20 Uhr', 'indoors': False}]'''

ex4 = '''(lo) In der heutigen Nacht wurde ein 59-jähriger Mann in der Altstadt von einem bislang unbekannten Täter angegriffen und lebensgefährlich verletzt. Die Polizei hat die Ermittlungen wegen eines versuchten Tötungsdeliktes aufgenommen. Nun sucht sie weitere Zeugen.
Gegen 00:50 Uhr fanden Passanten den 59-Jährigen stark blutend im Bereich der Neuen Kräme. Der daraufhin alarmierte Rettungswagen verbrachte den Geschädigten in ein umliegendes Krankenhaus. Hier konnten mehrere Einstichstellen im Oberkörper des Geschädigten festgestellt werden. Nach Angaben des Geschädigten befand er sich bis ca. 00.00 Uhr in einer Lokalität am Römerberg. Von hier aus sei er in Richtung Neue Kräme fußläufig unterwegs gewesen.
Aufgrund der schweren Verletzungen ermittelt die Frankfurter Mordkommission nun wegen eines versuchten Tötungsdelikts und sucht weitere Zeugen.'''
result4 = '''[{'crime': ['Tötungsdelikt',], 'location': 'Neue Kräme', 'time': '00:50 Uhr', 'indoors': False}]'''

ex5 = '''POL-F: 221118 - 1336 Frankfurt-Schwanheim: Passanten halten Räuber fest Frankfurt (ots) (dr) In der Nacht von Mittwoch auf Donnerstag (17. November 2022) kam es in Schwanheim zu einem Straßenraub, bei dem ein 47-jähriger Mann einer 18-Jährigen gewaltsam das Mobiltelefon entwendete. Mehrere Passanten zeigten Zivilcourage und hielten den Täter fest. Die 18-jährige Geschädigte und der 47-jährige Beschuldigte befanden sich zunächst in einem Bus der Linie 51 in Richtung Schwanheim. Bereits im Bus sprach der Mann die junge Frau an, die ihm jedoch signalisierte, an keinem Gespräch interessiert zu sein. Als der Bus gegen 0:45 Uhr in der Geisenheimer Straße an der Haltestelle Kelsterbach Weg anhielt und die Geschädigte ausstieg, folgte ihr der Beschuldigte. Plötzlich schlug ihr der Mann mit der Faust ins Gesicht, sodass die Geschädigte zu Boden fiel und sich leicht verletzte. Nach dem Sturz entriss ihr der 47-Jährige ihr Mobiltelefon und flüchtete mit diesem in westliche Richtung. Eine alarmierte Polizeistreife nahm den Mann fest und verbrachte ihn für die weiteren Maßnahmen auf die Polizeiwache. Gegen den 47-Jährigen wurde aufgrund des Straßenraubes ein Strafverfahren eingeleitet '''
result5 = '''[{'crime': ['Raub',], 'location': 'Geisenheimer Straße', 'time': '00:45 Uhr', 'indoors': False}]'''




'''
task = "Benenne für jeden Vorfall die Straftat, den Tatort, die Tatzeit (Uhrzeit) und ob die Straftat in einem Gebäude begangen wurde: "

ex1 = "Text: (th) Am Dienstag (22.11.2022) wurden zwei Crackdealer nach beobachteten Verkäufen festgenommen. Vormittags folgten zivile Polizeibeamte zwei Drogenkonsumenten vom Bahnhofsgebiet zum Schweizer Platz, wo sie auf ihren Dealer trafen und ca. 0,25 Gramm Crack in Empfang nahmen. Die beiden Käufer wurden vor Ort kontrolliert, der 42-jährige wohnsitzlose Dealer im Bereich Eschenheimer Tor festgenommen. Er führte weitere ca. 0,5 Gramm Crack bei sich, welche er versuchte zu schlucken. Ihm konnte ein weiterer Drogenhandel nachgewiesen werden, welcher einige Monate zurücklag. Es folgte die Einlieferung in das Zentrale Polizeigewahrsam zwecks Prüfung einer richterlichen Vorführung. Gegen 18:00 Uhr wurden Polizeibeamte auf einen weiteren Dealer im Bereich Am Hauptbahnhof aufmerksam. Sie identifizierten ihn als Verkäufer aus einem wenige Tage zuvor beobachteten Drogenhandel. Er wurde festgenommen. Gegen den ebenfalls 42-Jährigen Wohnsitzlosen bestand zudem ein offener Haftbefehl."
result1 = "[{'crime': ['Drogenhandel',], 'location': 'Schweizer Platz', 'time': 'Vormittag', 'indoors': False}, {'crime': ['Drogenhandel',], 'location': 'Am Hauptbahnhof', 'time': '18:00 Uhr', 'indoors': False}]"

ex2 = "Text: (dr) Eine Polizeistreife des 4. Reviers nahm am gestrigen Sonntag, den 20. November 2022, einen 19-Jährigen im Gutleutviertel fest, der sich bei einer Personenkontrolle besonders aggressiv zeigte. Bei ihm stellten sie auch Rauschgift sicher. Eine Ruhestörung in der Gutleutstraße führte gegen 22:10 Uhr zu einer Personenkontrolle eines 19-Jährigen. Der junge Mann war offensichtlich nicht mit der polizeilichen Maßnahme einverstanden und machte dies deutlich, indem er Tritte und Schläge gegen die ihn kontrollierenden Beamten austeilte. Währenddessen versuchte er auch immer wieder ein Einhandmesser aus seiner Jackentasche zu ziehen, was jedoch unterbunden werden konnte. Den Beamten gelang es, den 19-Jährigen unter Widerstand festzunehmen. Als sie ihn durchsuchten, stießen sie auf Betäubungsmittel, darunter rund 90 Gramm Amphetamin und über 90 Ecstasy-Tabletten. Bei einer anschließenden Durchsuchung an der Anschrift seiner Eltern fanden die Beamten in seinem "Kinderzimmer" weitere Substanzen zur Herstellung von Drogen auf sowie verbotene Gegenstände. Sie stellten alle Beweismittel sicher. Für den 19-Jährigen, welcher über keinen festen Wohnsitz verfügt, ging es in der Folge in die Haftzellen. Ihn erwartet nun ein Strafverfahren wegen des Verdachts des illegalen Drogenhandels und des Widerstands gegen Vollstreckungsbeamte. Er soll heute dem Haftrichter vorgeführt werden."
result2 = "[{'crime': ['Ruhestörung', 'Drogenhandel', 'Widerstand gegen Vollstreckungsbeamte',], 'location': 'Gutleutstraße', 'time': '22:10 Uhr', 'indoors': False}]"

ex3 = "Text: (wie) Ein berauschter Autofahrer ohne Führerschein ist in der Nacht von Freitag auf Samstag bei Hattersheim vor der Polizei geflohen, konnte aber festgenommen werden. Eine Streife der Autobahnpolizei wollte gegen 01:20 Uhr einen blauen Audi kontrollieren, da er mit eingeschalteter Nebelschlussleuchte auf der A 66 unterwegs war. Der Fahrer missachtete allerdings die Anhaltezeichen und wendete sein Fahrzeug, nachdem die Fahrzeuge bei Zeilsheim von der Autobahn abgefahren waren. Der Audi floh durch Zeilsheim und Sindlingen, überholte einen Linienbus mit hoher Geschwindigkeit und gefährdete in der Sindlinger Bahnstraße einen Fußgänger, der gerade einen Zebrastreifen nutzen wollte, aber rechtzeitig auf den Bürgersteig zurücktrat. Die Fahrt ging weiter bis nach Hattersheim, wo auch ein Fußgänger an einem Zebrastreifen gefährdet wurde. Schließlich konnte der Audi von Beamten der Autobahnpolizei und einem Frankfurter Streifenwagen gestoppt und der Fahrer festgenommen werden. Der 18-Jährige aus Straßburg stand offensichtlich unter dem Einfluss von Betäubungsmitteln und war nicht im Besitz einer Fahrerlaubnis."
result3 = "[{'crime': ['Fahren unter Drogeneinfluss', 'Fahren ohne Führerschein',], 'location': 'Hattersheim', 'time': '01:20 Uhr', 'indoors': False}]"

ex4 = "(lo) In der heutigen Nacht wurde ein 59-jähriger Mann in der Altstadt von einem bislang unbekannten Täter angegriffen und lebensgefährlich verletzt. Die Polizei hat die Ermittlungen wegen eines versuchten Tötungsdeliktes aufgenommen. Nun sucht sie weitere Zeugen. Gegen 00:50 Uhr fanden Passanten den 59-Jährigen stark blutend im Bereich der Neuen Kräme. Der daraufhin alarmierte Rettungswagen verbrachte den Geschädigten in ein umliegendes Krankenhaus. Hier konnten mehrere Einstichstellen im Oberkörper des Geschädigten festgestellt werden. Nach Angaben des Geschädigten befand er sich bis ca. 00.00 Uhr in einer Lokalität am Römerberg. Von hier aus sei er in Richtung Neue Kräme fußläufig unterwegs gewesen. Aufgrund der schweren Verletzungen ermittelt die Frankfurter Mordkommission nun wegen eines versuchten Tötungsdelikts und sucht weitere Zeugen."
result4 = "[{'crime': ['versuchtes Tötungsdelikt',], 'location': 'Neue Kräme', 'time': '00:50 Uhr', 'indoors': False}]"

ex5 = "18.11.2022 – 13:57 Polizeipräsidium Frankfurt am Main POL-F: 221118 - 1336 Frankfurt-Schwanheim: Passanten halten Räuber fest Frankfurt (ots) (dr) In der Nacht von Mittwoch auf Donnerstag (17. November 2022) kam es in Schwanheim zu einem Straßenraub, bei dem ein 47-jähriger Mann einer 18-Jährigen gewaltsam das Mobiltelefon entwendete. Mehrere Passanten zeigten Zivilcourage und hielten den Täter fest. Die 18-jährige Geschädigte und der 47-jährige Beschuldigte befanden sich zunächst in einem Bus der Linie 51 in Richtung Schwanheim. Bereits im Bus sprach der Mann die junge Frau an, die ihm jedoch signalisierte, an keinem Gespräch interessiert zu sein. Als der Bus gegen 0:45 Uhr in der Geisenheimer Straße an der Haltestelle Kelsterbach Weg anhielt und die Geschädigte ausstieg, folgte ihr der Beschuldigte. Hierbei kam ihr der 47-Jährige so nahe, dass die 18-Jährige sich umdrehte. Plötzlich schlug ihr der Mann mit der Faust ins Gesicht, sodass die Geschädigte zu Boden fiel und sich leicht verletzte. Nach dem Sturz entriss ihr der 47-Jährige ihr Mobiltelefon, das sie in der Hand hielt, und flüchtete mit diesem in westliche Richtung. Die Geschädigte rief nun lautstark um Hilfe, sodass mehrere Passanten auf die Situation aufmerksam wurden und den Räuber festhielten. Eine alarmierte Polizeistreife nahm den Mann fest und verbrachte ihn für die weiteren Maßnahmen auf die Polizeiwache. Gegen den 47-Jährigen wurde aufgrund des Straßenraubes ein Strafverfahren eingeleitet"
result5 = "[{'crime': ['Raub',], 'location': 'Geisenheimer Straße', 'time': '00:45 Uhr', 'indoors': False}]"
'''


prompt = task + "\n\n" + ex1 + "\n" + result1 + "\n" + "###" + "\n" + ex2 + "\n" + result2 + "\n" + "###" + "\n" + ex3 + "\n" + result3 + "\n" + "###" + "\n" + ex4 + "\n" + result4 + "\n" + "###" + "\n" + ex5 + "\n" + result5 + "\n" + "###" +  "\n"


def extract_crime_data(articles):
    crime_list = list()
    for idx in range(len(articles)):
        try:
            y = eval(GPT_Completion(api_key, prompt + articles[idx]["article"].replace("\n", " ").split("Rückfragen bitte an")[0]))
        except:
            y = [{'crime': [], 'location': None, 'time': None, 'indoors': False}]
        for d in y:
            cl = {"hq_id": articles[idx]["hq_id"],
                  "article_id": articles[idx]["id"],
                  "date": articles[idx]["date"],
                  "crime": d["crime"],
                  "location": d["location"],
                  "time": d["time"],
                  "indoors": d["indoors"]}
            crime_list.append(cl)
    return crime_list


crime_list = extract_crime_data(articles)

import pandas as pd

hq_id = [x["hq_id"] for x in crime_list]
id_ = [x["article_id"] for x in crime_list]
date = [x["date"] for x in crime_list]
crime = [x["crime"] for x in crime_list]
location = [x["location"] for x in crime_list]
time = [x["time"] for x in crime_list]
indoors = [x["indoors"] for x in crime_list]

df2 = pd.DataFrame({"hq_id": hq_id,
                  "article_id": id_,
                  "date": date,
                  "crime": crime,
                  "location": location,
                  "time": time,
                  "indoors": indoors})

crimes = ", ".join(set([i for x in crime_list for i in x["crime"]]))

[article for article in articles if article["id"] == "5384331"]

from transformers import BloomForCausalLM
from transformers import BloomTokenizerFast

model = BloomForCausalLM.from_pretrained("bigscience/bloom-560m")
tokenizer = BloomTokenizerFast.from_pretrained("bigscience/bloom-560m")

prompt = "It was a dark and stormy night"
result_length = 254
inputs = tokenizer(prompt, return_tensors="pt")

# Greedy Search
print(tokenizer.decode(model.generate(inputs["input_ids"],
                       max_length=result_length
                      )[0]))

# Beam Search
print(tokenizer.decode(model.generate(inputs["input_ids"],
                       max_length=result_length,
                       num_beams=2,
                       no_repeat_ngram_size=2,
                       early_stopping=True
                      )[0]))

# Sampling Top-k + Top-p
print(tokenizer.decode(model.generate(inputs["input_ids"],
                       max_length=result_length,
                       do_sample=True,
                       top_k=50,
                       top_p=0.9
                      )[0]))








from transformers import AutoModelForCausalLM, AutoTokenizer

#checkpoint = "bigscience/bloomz-7b1-mt"
checkpoint = "bigscience/bloom-7b1"
checkpoint = "bigscience/bloomz-3b"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint)

prompt = "Translate to English: Je t’aime."
inputs = tokenizer.encode(prompt, return_tensors="pt")
outputs = model.generate(inputs)
print(tokenizer.decode(outputs[0]))









import requests

TOKEN = "Bearer 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"

API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
API_URL = "https://api-inference.huggingface.co/models/facebook/opt"
headers = {"Authorization": TOKEN}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response


prompt = task + "\n\n" + ex1 + "\n" + result1 + "\n" + ex2[:1259] + "\n" + result2 + "\n" + "###" + "\n" + ex3 + "\n" + result3 + "\n" + "###" + "\n" + ex4 + "\n" + result4 + "\n" + "###" + "\n" + ex5 + "\n" + result5 + "\n" + "###" +  "\n"

#prompt = "Translate to German: \n I love you = Ich liebe dich \n I hate you = Ich hasse dich \n I like you = "

output = query({
    "inputs": prompt,
    "parameters": {"max_new_tokens": 30,
                   "return_full_text": False,
                   "do_sample": False}
})

print(output.text)