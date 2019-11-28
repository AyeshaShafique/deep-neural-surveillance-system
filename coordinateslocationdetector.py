import requests
import json


class CoordinatesLocationDetector:
    
    def __init__(self, send_url='http://api.ipstack.com/39.48.169.175?access_key=b9e1745db2b7e9f293b874afe6d6bd7f'):
        self.send_url=send_url
        
    def get_location_coordinates(self):
        r = requests.get(self.send_url)
        j = json.loads(r.text)
        lat = j['latitude']
        lon = j['longitude']
        zipcode = j['zip']
        
        return (lat, lon, zipcode)
        

