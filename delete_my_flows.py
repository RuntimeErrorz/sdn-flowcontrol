from requests.auth import HTTPBasicAuth
from find_another_way import loadmap
from controller import del_groups_by_dev_id_app_cookie, del_flows_by_app_id
ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")

devices = loadmap('devices', 'links', 'hosts')[2]


if __name__ == '__main__':
    list = ["my_app","block"]
    for i in list:
        print(del_flows_by_app_id(ip, i))
    app_cookie = "0x1234"
    for device in devices:
        print(del_groups_by_dev_id_app_cookie(ip, device['id'], app_cookie))
