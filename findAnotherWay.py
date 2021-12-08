import json
from controller import add_flow, get_criteria, add_group_table
ip = "127.0.0.1"

arpInstruction = [{"type": "OUTPUT","port": "NORMAL"}]
arpCriteria = [{"type": "ETH_TYPE","ethType": "0x0806"}]

def loadmap(devices, links, hosts):
    with open(str(devices)+".json", 'r') as j:
        ls = json.load(j)
    length = len(list(ls.values())[0])
    devices = list(ls.values())[0]
    with open(str(links)+".json", 'r') as k:
        linksls = json.load(k)
    with open(str(hosts)+".json", 'r') as h:
        hostsls = json.load(h)
    hosts = list(hostsls.values())[0]
    map = [[float('inf') for i in range(length)] for i in range(length)]
    LinksList = list(linksls.values())[0]
    for link in LinksList:
        src = (int(link['src']['device'][3:], 16)) - 1
        dst = (int(link['dst']['device'][3:], 16)) - 1
        map[src][dst] = 1
    return map, LinksList, devices, hosts

map, links, devices, hosts = loadmap('devices', 'links', 'hosts')

def Dijkstra(src, dsts):
    length = len(map)
    visited = [False for i in range(length)]
    path = [-1 for i in range(length)]
    finalPaths = [[]for _ in range(len(dsts))]
    distance = [float('inf') for _ in range(length)]
    distance[src - 1] = 0
    while True:
        v = -1
        for u in range(length):
            if not visited[u] and (v == -1 or distance[u] < distance[v]):
                v = u
        if v == -1:
            break
        visited[v] = True
        for u in range(length):
            if distance[v] + map[v][u] < distance[u]:
                path[u] = v
            distance[u] = min(distance[u], distance[v] + map[v][u])
    for (finalPath,dst) in zip(finalPaths,dsts):
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
    add_flow(ip, srcId, 'myApp',arpInstruction, arpCriteria)
    add_flow(ip, dstId, 'myApp',arpInstruction, arpCriteria)
    path = Dijkstra(src, [dst])[0]
    print(path)
    linkAllbyPath(ip_protocol, path, lastPort,port_dst, mac_src, mac_dst)


def get_group_instructions(list):
    return [{"type": "OUTPUT","port": int(i)} for i in list]


def get_deviceID(src):
    src = str(hex(src))[2:]
    list = ['0' for _ in range(16 - len(src))]
    list.append(src)
    list.insert(0, 'of:')
    return ''.join(list)


def get_ports(ID1, ID2):
    for link in links:
        if link['src']['device'] == ID1 and link['dst']['device'] == ID2:
            return link['src']['port'], link['dst']['port']


def longestCommonPrefix(lists):
    res = []
    for tmp in zip(*lists):
        tmp_set = set(tmp)
        if len(tmp_set) == 1:
            res.append(tmp[0])
        else:
            break
    return res


def linkAllbyPath(ip_protocol ,path, lastPort, port_dst, mac_src, mac_dst = "optional", flag = 1):
    for i in range(len(path) - 1):
        ID1 = get_deviceID(path[i])
        ID2 = get_deviceID(path[i+1])
        add_flow(ip, ID1, 'myApp',arpInstruction, arpCriteria)
        port_src = port_dst
        port_dst, _ = get_ports(ID1, ID2)
        print(port_src, port_dst)
        instruction1 = [{"type": "OUTPUT","port": port_dst}]
        criteria1 = get_criteria(ip_protocol,port_src, mac_src, mac_dst = mac_dst)
        if mac_dst == "optional":
                    criteria1 = criteria1[:-1]
        add_flow(ip, ID1, "myApp", instruction1, criteria1)
        if flag == 1:
            instruction2 = [{"type": "OUTPUT","port": port_src}]
            criteria2 = get_criteria(ip_protocol,port_dst, mac_dst, mac_dst = mac_src)
            add_flow(ip, ID1, "myApp", instruction2, criteria2)
        port_src, port_dst = get_ports(ID1, ID2)
    port_src = port_dst
    port_dst = lastPort
    print(port_src, port_dst)
    criteria1 = get_criteria(ip_protocol, port_src,mac_src, mac_dst = mac_dst)
    instruction1 = [{"type": "OUTPUT","port": port_dst}]
    if mac_dst == "optional":
        criteria1 = criteria1[:-1]
    add_flow(ip, ID2, "myApp", instruction1, criteria1)
    if flag == 1:
        instruction2 = [{"type": "OUTPUT","port": port_src}]
        criteria2 = get_criteria(ip_protocol, port_dst, mac_dst, mac_dst = mac_src)
        add_flow(ip, ID2, "myApp", instruction2, criteria2)



def findAnotherWays(ip_protocol, src, dsts):
    mac_dsts = []
    lastPorts =[]
    dstIds = []
    dstss = []
    for host in hosts:
        if host['id'] == src:
            mac_src = host['mac']
            port_dst = host['locations'][0]['port']
            srcId = host['locations'][0]['elementId']
            src = int(host['locations'][0]['elementId'][3:], 16)
        for dst in dsts:
            if host['id'] == dst:
                mac_dsts.append(host['mac'])
                lastPorts.append(host['locations'][0]['port'])
                dstIds.append (host['locations'][0]['elementId'])
                dstss.append(int(host['locations'][0]['elementId'][3:], 16))
    add_flow(ip, srcId, 'myApp',arpInstruction, arpCriteria)
    for dstId in dstIds:
        add_flow(ip, dstId, 'myApp',arpInstruction, arpCriteria)
    paths = Dijkstra(src, dstss)
    print(paths)
    commonPath = longestCommonPrefix(paths)
    merge_point = commonPath[-1]
    merge_id = get_deviceID(merge_point)
    tmpP = commonPath[-2]
    _, last_port = get_ports(get_deviceID(tmpP), merge_id)
    instructions = [{"type": "GROUP","groupId": 1}]
    criteria = get_criteria(ip_protocol, last_port, mac_src)[:-1]
    print(criteria)
    individualPaths = []
    for path in paths:
        individualPaths.append(path[len(commonPath):])
    outports = [get_ports(merge_id, get_deviceID(i[0]))[0] for i in individualPaths]  
    print(outports)
    print(get_group_instructions(outports))
    add_group_table(ip,merge_id,1,"0x1234",get_group_instructions(outports))
    add_flow(ip,merge_id,"myApp",instructions,criteria)
    linkAllbyPath(ip_protocol, commonPath[:-1], last_port, port_dst, mac_src, flag = 0)
    print("------------------")
    print(individualPaths)
    for (individualPath, lastport, mac_dst) in zip(individualPaths, lastPorts, mac_dsts):
        _ , port_dst = get_ports(merge_id, get_deviceID(individualPath[0]))
        linkAllbyPath(ip_protocol, individualPath, lastport, port_dst, mac_src, mac_dst, flag = 0)
        print("--------------")


# findAnotherWay(1, '00:00:00:00:00:01/None', '00:00:00:00:00:03/None')
# findAnotherWay(1, '00:00:00:00:00:01/None', '00:00:00:00:00:02/None')


findAnotherWays(17, '00:00:00:00:00:01/None', ['00:00:00:00:00:03/None','00:00:00:00:00:02/None'])