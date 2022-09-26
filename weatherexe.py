# folium main map program very easy to use, requests gets data from online sources
import requests, folium
# pandas to deal with csv file data
import pandas as pd
# to open the map when done
import webbrowser
# to get location data based on a city name (long and lat)
from geopy.geocoders import Nominatim
#allows for multpile processes to be run at once (this program would take hours to run otherwise)
import threading
#for file managent and clear() function
import os
#manages json files recieved from api requsts
import json
#imports specific elements from the modules to help with other apspects
from os import system,name
from folium import plugins
from folium.plugins import MarkerCluster
#the basic ones
import datetime, math, time

#start client for geoloactor
geolocator = Nominatim(user_agent="I'm the map - Dora")
#define map to which we will be ading things to
the_map_dora = folium.Map(location = [0,0], zoom_start = 2.5, tiles = 'OpenStreetMap')
#add different styles of map so the user can select the one that best fits them
folium.TileLayer('Stamen Terrain').add_to(the_map_dora)
folium.TileLayer('Stamen Toner').add_to(the_map_dora)
folium.TileLayer('Stamen Water Color').add_to(the_map_dora)
folium.TileLayer('cartodbpositron').add_to(the_map_dora)
folium.TileLayer('cartodbdark_matter').add_to(the_map_dora)
folium.LayerControl().add_to(the_map_dora)

#add title to the map which represents when the map was updated
datetime_cur = datetime.datetime.now()
name1 = f'Last updated: {datetime_cur.month}/{datetime_cur.day}/{datetime_cur.year}, {datetime_cur.hour}:{datetime_cur.minute} EST'
title_html = '''
             <p align="center" style="font-size:10px"><b>{}</b></p>
             '''.format(name1)
the_map_dora.get_root().html.add_child(folium.Element(title_html))

#initiats lableclustering for later purposes
cluster = MarkerCluster(control=False).add_to(the_map_dora)

#reads location.csv to get locations of cities quicker
latlong = pd.read_csv('location4.csv', index_col=[0])
cities = list(latlong.index)

#clears the console when called
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
clear()

#splits the huge list named cities into 'lst' sized chunks for multithreading
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#define how many processes you want running at once (283 has been determined to be optimal)
thread_count = 283

#gets a value that will split the length of the cities list into 'thread_count' number of equal parts
split_num = int(math.ceil(len(cities)/thread_count))
#puts every threads' list into one list
masterlist = list(chunks(cities, split_num))
#kill switch for threads
stop_threads = False

#master variable to the main thread can kill the others when x reaches a certain number
global x
x = 0

class Weather:
    #does the following: gets longitude and latitude for ever city in the master list, gets weather data for each city, adds the city maker and weather data to the map
    def get_weather_data(self,location, number, key):
        #sends a requsts to weatherapi.com
        r = requests.get(f"https://api.weatherapi.com/v1/forecast.json?key={key}&q={location}&days=10")
        #converts the json file returned by the website to a dictionary
        content = json.loads(r.content)
        #defins things...

        currenttemp = str(content['current']['temp_f'])+'°F'
        location = {
        'city' : content['location']['name'],
        'region' : content['location']['region'],
        'country' : content['location']['country']
        }
        timeupdated = str(content['current']['last_updated'].split()[1])
        chance_percip = str(content['forecast']['forecastday'][0]['day']['daily_chance_of_rain']) + '%'
        high = str(content['forecast']['forecastday'][0]['day']['maxtemp_f'])+'°F'
        low = str(content['forecast']['forecastday'][0]['day']['mintemp_f'])+'°F'
        return {'currenttemp':currenttemp, 'location':location,'timeupdated':timeupdated,'chance_percip':chance_percip,'high':high,'low':low}
    #returns weather data dictionary given a longitude and latitude
    def main_task(self,cities,number,keyNum):
        global x
        for city in cities:
            #kill switch for all threads
            if stop_threads:
                break
            #try and except bc some cities arent alwasy findable or don't have weather data
            try:
                #gets latitude and longitude
                lat = latlong['latitude'].loc[city]
                long = latlong['longitude'].loc[city]
                #gets weather data from above function
                popup_dict = Weather().get_weather_data(city,number,keyNum)
                #html formats the data into something readable
                popup_format = f"""
                <center>
                <h4>Temp: {popup_dict['currenttemp']}</h4>
                <strong>High: {popup_dict['high']}, Low: {popup_dict['low']}</strong><br>
                Chance Percip: {popup_dict['chance_percip']}<br>
                Local Time: {popup_dict['timeupdated']}
                </center>
                """
                #defins the popup the user will see when they click on a city marker.
                popup = folium.Popup(popup_format, max_width = 200, parse_html = False)
                #adds a makrer at the latitude and longitude location with the above data embeded
                folium.CircleMarker(location=[lat, long], radius=1, weight=5,popup=popup, tooltip=city, name = city).add_to(cluster)
            except:
                pass
            x+=1


#asigns api keys and lists of citiess to each thread and a number to reference each thread individually
step = int(round(thread_count/4, 0))
threads = []
for i in range(0, len(masterlist), 1):
    if i < step:
        key = "d02507ee71f449fc8ac161147212510"
    elif i < step*2:
        key = "099803e0610a4f1d8ee184704212911"
    elif i < step*3:
        key = "d1a6c79ea5a146c3ac1184935212911"
    elif i <= step*4:
        key = "9f8a28e558e04d04b55182838210712"
    #weather api keys (we needed more than one to speed things up)
    #other keys
    #   5e5a2899c6484ce9915185829210712
    #   459695e179d942c7869185539210712
    threads.append(threading.Thread(target=Weather().main_task, args = (masterlist[i],i,key,)))

#starts all threads
for thread in threads:
    thread.start()

#waits for threads to be finished4
while x < len(cities)-20:
    #cool loading bar
    print(f"Loading Weather data...  {round((x/(len(cities)-3))*100,4)}%   {x}",end = "                           \r")
print("Loading Weather data...  100.0%   ",end = "                           \r")
clear()
print('Finalizing....')
#stops threads and ensures that they are finsished
stop_threads = True
for thread in threads:
    thread.join()

#opens the final file
the_map_dora.save("map.html")
clear()
webbrowser.open('map.html')
print('Done!')
