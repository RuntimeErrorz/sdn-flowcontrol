import requests
from requests.auth import HTTPBasicAuth
ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")

def del_flows_by_appId(controller_ip, appId):
    headers = {
        'Accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/application/{}'.format(controller_ip, appId)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code, resp.text

def del_groups_by_devId_appCookie(controller_ip, devId, appCookie):
    headers = {
        'Accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}/{}'.format(controller_ip, devId, appCookie)
    print(get_device_url)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code

if __name__ == '__main__':
    list = ["org.onosproject.core", "myApp", "org.onosproject.fwd"]
    for i in list:
        status_code, resp = del_flows_by_appId(ip, i)
        print(status_code)
    devId =["of:0000000000000001", "of:0000000000000005"]
    appCookie = "0x1234"
    for i in devId:
        print(del_groups_by_devId_appCookie(ip, i, appCookie))

