# 更新

1. 新增blockFwd.py，deleteMyflows来替代deleteAll.py的功能。
2. 修复组播功能并实现真正的组播。
3. 具体新增操作加粗表示。**请注意查看加粗部分。**

# 创建数据
先运行onos，使用ssh连接上最后使用Mininet创建拓扑并连接远程控制器。切记运行如下命令。

```shell
mininet> pingall
```

运行get.py，得到三个json文件。

```shell
python3 get.py
```

# 屏蔽流表组表

**运行blockFwd.py**

```shell
python3 blockFwd.py
```

# 下发流表组表
运行findAnotherWay.py，其中单播使用pingall展示，因此添加了双向流表。组播使用udp播放视频展示。单播为findAnotherWay()，组播为findAnotherWays()。可以自行修改参数。值得注意的是这两个函数的第一个形参为IP协议号，udp为17，ICMP为1。播放视频参照步骤参考 https://uestc.feishu.cn/docs/doccnzdEiVYzfBOV4Dspc8fMHie#WgGz2W 中的4.2一节操作。**现在的组播操作只需要源主机向目的主机的第一个发出UDP包即可。举例：**

```python
findAnotherWays(17, '00:00:00:00:00:03/None',
                    ['00:00:00:00:00:01/None', '00:00:00:00:00:02/None'])
```

**此时只需要源主机h3向目的主机h1发送视频即可，h2便可以自动收到。**

```shell
python3 findAnotherWay.py
```

# 删除自己下发的流表

**运行deleteMyFlows.py，再演示不同的起始点和终止点时可以删除一下。（虽然不删除也没啥问题）**

```
python3 deleteMyFlows.py
```

# 可能有的Bug

1. 当组播点为第一个交换机时会触发数组越界，这种情况应该使用多次单播，findAnotherWay(17, src)。（强行Feature）
2. 有时候组表添加后状态不是 "ADDED"，而是 “PENDING_ADD_RETRY”，复现条件应该是建立两次不同的拓扑，重启解。
3. **有时候组播可能不成功，可能是因为ONOS反应缓慢，只需要再执行一次就好了。**

# 未来计划

1. 实际上这种方案并不是最节省流量的，组播时应该有多个组播点。（不过这个例子组播对象只有两个）可以进行改进。
2. **交换机down、链路down、轮询、比较区别、意图感知，基于时延选路**。
3. Java插件开发看情况。

