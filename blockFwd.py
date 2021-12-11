from findAnotherWay import loadmap
from controller import block_fwd

ip = "127.0.0.1"

devices = loadmap('devices', 'links', 'hosts')[2]

for device in devices:
    block_fwd(ip, "block", device['id'])