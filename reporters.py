import json
import requests


class HttpReporter:
    def __init__(self,url):
        self._url = url
    
    def send(self, data):
        try:
          resp = requests.post(url = self._url, data = data)
        except:
          raise ConnectionError("Could not send message")
        
        if resp.status_code != 200:
          raise ValueError("Message not processed in destination")


class HttpReporterForDebug:
    def __init__(self,url):
        self._url = url
    
    def send(self, data):
        d = json.loads(data)
        try:
          requests.post(url = self._url, data = data)
          print(f'message sent {d["timestamp"]}')
        except:
                print(f'message NOT sent {d["timestamp"]}')
                raise ConnectionError("Could not send message")