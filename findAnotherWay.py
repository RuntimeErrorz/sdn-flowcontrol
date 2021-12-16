import json
from controller import *
ip = "127.0.0.1"
import heapq

arpInstruction = [{"type": "OUTPUT", "port": "NORMAL"}]
arpCriteria = [{"type": "ETH_TYPE", "ethType": "0x0806"}]


def loadmap(devices, links, hosts):
    with open(str(devices)+".json", 'r') as j:
        ls = json.load(j)
    length = len(list(ls.values())[0])
    devices = list(ls.values())[0]
    downDevices = []
    i = 0
    temp = length
    while i < temp:
        if not devices[i]["available"]:
            downDevices.append(devices[i]["id"])
            del(devices[i])
            temp -= 1
            continue
        else:
            i += 1
    with open(str(links)+".json", 'r') as k:
        linksls = json.load(k)
    with open(str(hosts)+".json", 'r') as h:
        hostsls = json.load(h)
    hosts = list(hostsls.values())[0]
    map = [[float('inf') for i in range(length)] for i in range(length)]
    for i in range(length):
        map[i][i] = 0
    LinksList = list(linksls.values())[0]
    for link in LinksList:
        srcId = link['src']['device']
        dstId = link['dst']['device']
        if srcId in downDevices or dstId in downDevices:
            continue
        src = (int(srcId[3:], 16)) - 1
        dst = (int(dstId[3:], 16)) - 1
        map[src][dst] = 1
    return map, LinksList, devices, hosts


if __name__ == "__main__":
    map, links, devices, hosts = loadmap('devices', 'links', 'hosts')


def heapyDijkstra(src, dsts):
    length = len(map)
    path = [-1 for i in range(length)]
    finalPaths = [[]for _ in range(len(dsts))]
    distance = [float('inf') for _ in range(length)]
    distance[src - 1] = 0
    for i in range(length):
        distance[i] = map[src-i][i]
    queue = []
    heapq.heapify(queue)
    heapq.heappush(queue, distance[src-1])
    while queue:
        v = heapq.heappop(queue)
        for u in range(length):
            if distance[v] + map[v][u] < distance[u]:
                path[u] = v
                distance[u] = distance[v] + map[v][u]
                heapq.heappush(queue,distance[u])
    for (finalPath, dst) in zip(finalPaths, dsts):
        finalPath.append(dst)
        p = dst - 1
        while path[p] != -1:
            finalPath.append(path[p] + 1)
            p = path[p]
    for i in range(len(finalPaths)):
        finalPaths[i] = list(reversed(finalPaths[i]))
    return finalPaths


def findAnotherWay(ip_protocol, src, dst):
    for host in hosts:
        if host['id'] == src:
            mac_src = host['mac']
            port_dst = host['locations'][0]['port']
            srcId = host['locations'][0]['elementId']
            src = int(host['locations'][0]['elementId'][3:], 16)
        if host['id'] == dst:
            mac_dst = host['mac']
            lastPort = host['locations'][0]['port']
            dstId = host['locations'][0]['elementId']
            dst = int(host['locations'][0]['elementId'][3:], 16)
    add_flow(ip, srcId, 'myApp', arpInstruction, arpCriteria)
    add_flow(ip, dstId, 'myApp', arpInstruction, arpCriteria)
    path = heapyDijkstra(src, [dst])[0]
    print(path)
    linkAllbyPath(ip_protocol, path, lastPort,
                  port_dst, mac_src, mac_dst=mac_dst)


def linkAllbyPath(ip_protocol, path, lastPort, port_dst, mac_src, temp_port=-1, mac_dst="optional", flag=1):
    if (len(path) == 1):
        print(port_dst, temp_port)
        ID1 = get_deviceID(path[0])
        add_flow(ip, ID1, 'myApp', arpInstruction, arpCriteria)
        instruction1 = [{"type": "OUTPUT", "port": temp_port}]
        criteria1 = get_criteria(
            ip_protocol, port_dst, mac_src, mac_dst=temp_port)
        add_flow(ip, ID1, "myApp", instruction1, criteria1)
        return

    for i in range(len(path) - 1):
        ID1 = get_deviceID(path[i])
        ID2 = get_deviceID(path[i+1])
        add_flow(ip, ID1, 'myApp', arpInstruction, arpCriteria)
        port_src = port_dst
        port_dst, _ = get_ports(ID1, ID2, links)
        print(port_src, port_dst)
        instruction1 = [{"type": "OUTPUT", "port": port_dst}]
        criteria1 = get_criteria(
            ip_protocol, port_src, mac_src, mac_dst=mac_dst)
        if mac_dst == "optional":
            criteria1 = criteria1[:-1]
        add_flow(ip, ID1, "myApp", instruction1, criteria1)
        if flag == 1:
            instruction2 = [{"type": "OUTPUT", "port": port_src}]
            criteria2 = get_criteria(
                ip_protocol, port_dst, mac_dst, mac_dst=mac_src)
            add_flow(ip, ID1, "myApp", instruction2, criteria2)
        port_src, port_dst = get_ports(ID1, ID2, links)

    port_src = port_dst
    port_dst = lastPort
    add_flow(ip, ID2, "myApp", arpInstruction, arpCriteria)
    print(port_src, port_dst)
    criteria1 = get_criteria(ip_protocol, port_src, mac_src, mac_dst=mac_dst)
    instruction1 = [{"type": "OUTPUT", "port": port_dst}]
    if mac_dst == "optional":
        criteria1 = criteria1[:-1]
    add_flow(ip, ID2, "myApp", instruction1, criteria1)
    if flag == 1:
        instruction2 = [{"type": "OUTPUT", "port": port_src}]
        criteria2 = get_criteria(
            ip_protocol, port_dst, mac_dst, mac_dst=mac_src)
        add_flow(ip, ID2, "myApp", instruction2, criteria2)


def findAnotherWays(ip_protocol, src, dsts):
    mac_dsts = []
    lastPorts = []
    dstIds = []
    dstss = []
    ips = []
    for host in hosts:
        if host['id'] == src:
            mac_src = host['mac']
            port_dst = host['locations'][0]['port']
            srcId = host['locations'][0]['elementId']
            src = int(host['locations'][0]['elementId'][3:], 16)
    for dst in dsts:
        for host in hosts:
            if host['id'] == dst:
                mac_dsts.append(host['mac'])
                ips.append(host['ipAddresses'][0])
                lastPorts.append(host['locations'][0]['port'])
                dstIds.append(host['locations'][0]['elementId'])
                dstss.append(int(host['locations'][0]['elementId'][3:], 16))
    add_flow(ip, srcId, 'myApp', arpInstruction, arpCriteria)
    for dstId in dstIds:
        add_flow(ip, dstId, 'myApp', arpInstruction, arpCriteria)
    paths = heapyDijkstra(src, dstss)
    print(paths)
    commonPath = longestCommonPrefix(paths)
    print(commonPath)
    merge_point = commonPath[-1]
    merge_id = get_deviceID(merge_point)
    tmpP = commonPath[-2]
    temp_port, last_port = get_ports(get_deviceID(tmpP), merge_id, links)
    instructions = [{"type": "GROUP", "groupId": 1}]
    criteria = get_criteria(ip_protocol, last_port, mac_src)[:-1]
    individualPaths = []
    for path in paths:
        individualPaths.append(path[len(commonPath):])
    print(individualPaths)
    outports = [get_ports(merge_id, get_deviceID(i[0]), links)[0]
                for i in individualPaths]
    add_group_table(ip, merge_id, 1, "0x1234",
                    get_group_buckets(ips, mac_dsts, outports))
    add_flow(ip, merge_id, "myApp", instructions, criteria)
    add_flow(ip, merge_id, "myApp", arpInstruction, arpCriteria)
    linkAllbyPath(ip_protocol, commonPath[:-1],
                  last_port, port_dst, mac_src, temp_port=temp_port, flag=0)
    print("------------------")
    for (individualPath, lastport, mac_dst) in zip(individualPaths, lastPorts, mac_dsts):
        print(mac_src, mac_dst)
        temp_port, port_dst = get_ports(
            merge_id, get_deviceID(individualPath[0]), links)
        linkAllbyPath(ip_protocol, individualPath, lastport,
                      port_dst, mac_src, temp_port=temp_port, mac_dst=mac_dst, flag=0)
        print("--------------")


if __name__ == "__main__":
    pass
    # findAnotherWay(1, '00:00:00:00:00:01/None', '00:00:00:00:00:03/None')
    # findAnotherWay(1, '00:00:00:00:00:01/None', '00:00:00:00:00:02/None')
    # findAnotherWays(17, '00:00:00:00:00:03/None',
    #                 ['00:00:00:00:00:01/None', '00:00:00:00:00:02/None'])
