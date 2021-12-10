import requests
import json
from requests.auth import HTTPBasicAuth

ip="127.0.0.1"
auth = HTTPBasicAuth("karaf","karaf")
headers = {'Accept':'application/json'}

def get(type):
    get_url = 'http://{}:8181/onos/v1/{}'.format(ip, type)
    print(get_url)
    resp = requests.get(url = get_url,headers =headers,auth = auth )
    return resp.status_code,resp.text

if __name__ == '__main__':
    list=['links', 'devices', 'hosts']
    for i in list:
        status_code,resp = get(i)
        print(status_code)
        if status_code == 200:
            contents = json.loads(resp)
            with open(i + '.json','w') as j:
                j.write(json.dumps(contents, indent=2))