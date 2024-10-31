import requests

class volumio:
    volumio_url = None
    
    def __init__(self, url):
        self.volumio_url = "{}/api/v1".format(url)

    def status(self):
        res = requests.get("{}/getState".format(self.volumio_url))
        return res.json()

    def volume(self, volume):
        requests.get("{}/commands/?cmd=volume&volume={}".format(self.volumio_url, volume))
        self.status()

    def volume_increase(self):
        requests.get("{}/commands/?cmd=volume&volume=plus".format(self.volumio_url))
        self.status()

    def volume_minus(self):
        requests.get("{}/commands/?cmd=volume&volume=minus".format(self.volumio_url))
        self.status()

    def playlist(self, playlist):
        requests.get("{}/commands/?cmd=playplaylist&name={}".format(self.volumio_url, playlist))
        self.status()

    def playback(self, data):
        json_data = {
            "item": data,
            "list": [ data ],
            "index": 0
        }
        
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post("{}/replaceAndPlay".format(self.volumio_url), json=json_data, headers=headers)
        self.status()

    def command(self, command, callback = None):
        requests.get("{}/commands/?cmd={}".format(self.volumio_url, command))
        if callback != None:
            callback()
        else:
            self.status()
