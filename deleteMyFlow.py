import requests
from requests.auth import HTTPBasicAuth
ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")


def del_flows_by_appId(controller_ip, appId):
    headers = {
        'Accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/application/{}'.format(
        controller_ip, appId)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code


def del_groups_by_devId_appCookie(controller_ip, devId, appCookie):
    headers = {
        'Accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}/{}'.format(
        controller_ip, devId, appCookie)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code


if __name__ == '__main__':
    list = ["myApp","block"]
    for i in list:
        print(del_flows_by_appId(ip, i))
    devId = ["of:0000000000000005"]
    appCookie = "0x1234"
    for i in devId:
        print(del_groups_by_devId_appCookie(ip, i, appCookie))
