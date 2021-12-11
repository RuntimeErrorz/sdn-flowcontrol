from requests.auth import HTTPBasicAuth
from findAnotherWay import loadmap
from controller import del_groups_by_devId_appCookie, del_flows_by_appId
ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")

devices = loadmap('devices', 'links', 'hosts')[2]


if __name__ == '__main__':
    list = ["myApp","block"]
    for i in list:
        print(del_flows_by_appId(ip, i))
    appCookie = "0x1234"
    for device in devices:
        print(del_groups_by_devId_appCookie(ip, device['id'], appCookie))
