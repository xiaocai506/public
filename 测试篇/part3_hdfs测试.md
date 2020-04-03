# HDFS性能对比测试

## 一、机器

参考[part1_硬件性能测试](./part1_硬件性能测试.md)

## 二、服务配置

相关配置文件见目录[hdfs相关配置文件](./files/hdfs/conf)

！！！机器给自己做下免密设置，可参考链接https://blog.csdn.net/hellopeng1/article/details/80658359

## 三、测试方案

采用HiBench测试框架，版本号：7.1-SNAPSHOT 2的改造版。

###适配ZFM的相关配置（157.111）

相关配置见目录[hdfs配置文件目录](./files/hibench/zfm)

### 适配CM的相关配置（157.110）

相关配置见目录[hdfs配置文件目录](./files/hibench/cm/)

## 四、测试用例

### 用例1：workload Sort

hibench 默认配置

#### CM：157.110

```shell
#数据准备
[root@lv110 HiBench]# bin/workloads/micro/sort/prepare/prepare.sh 
#测试运行
[root@lv110 HiBench]# bin/workloads/micro/sort/hadoop/run.sh 
#报告见
[root@lv110 HiBench]# vim report/hibench.report 
```

#### ZFM：157.111

```shell
#数据准备
[root@lv111 HiBench]# bin/workloads/micro/sort/prepare/prepare.sh 
#运行
[root@lv111 HiBench]# bin/workloads/micro/sort/hadoop/run.sh 

```



### 用例2：workload WordCount

hibench默认配置

#### CM：157.110

```shell
#数据准备
[root@lv110 HiBench]# bin/workloads/micro/wordcount/prepare/prepare.sh 
#运行
[root@lv110 HiBench]# bin/workloads/micro/wordcount/hadoop/run.sh 
```

#### ZFM：157.111

```shell
#数据准备
[root@lv111 HiBench]# bin/workloads/micro/wordcount/prepare/prepare.sh 
#运行
[root@lv111 HiBench]# bin/workloads/micro/wordcount/hadoop/run.sh 
```

### 用例3：workload TeraSort

#### CM：157.110

```shell
#数据准备
[root@lv110 HiBench]# bin/workloads/micro/terasort/prepare/prepare.sh
#运行
[root@lv110 HiBench]# vim bin/workloads/micro/terasort/hadoop/run.sh 
```

#### ZFM：157.111

```shell
#数据准备
[root@lv111 HiBench]# bin/workloads/micro/terasort/prepare/prepare.sh
#运行
[root@lv111 HiBench]# bin/workloads/micro/terasort/hadoop/run.sh
```

### 用例4：workload Sleep

#### CM：157.110

```shell
#数据准备
[root@lv110 HiBench]# bin/workloads/micro/sleep/prepare/prepare.sh
#运行
[root@lv110 HiBench]# bin/workloads/micro/sleep/hadoop/run.sh
```

#### ZFM：157.111

```shell
#数据准备
[root@lv111 HiBench]# bin/workloads/micro/sleep/prepare/prepare.sh 
#运行
[root@lv111 HiBench]# bin/workloads/micro/sleep/hadoop/run.sh 
```

### 用例5：workload enhanced DFSIO

#### CM：157.110

```shell
#数据准备
[root@lv110 HiBench]# bin/workloads/micro/dfsioe/prepare/prepare.sh
#运行
[root@lv110 HiBench]# bin/workloads/micro/dfsioe/hadoop/run.sh 
```

#### ZFM：157.111

```shell
#数据准备
[root@lv111 HiBench]# bin/workloads/micro/dfsioe/prepare/prepare.sh 
#运行
[root@lv111 HiBench]# bin/workloads/micro/dfsioe/hadoop/run.sh 
```



## 五、测试结果

### CM：157.110

| Type               | Date      | Time     | Input_data_size | Duration(s) | Throughput(bytes/s) | Throughput/node |
| ------------------ | --------- | -------- | --------------- | ----------- | ------------------- | --------------- |
|                    |           |          |                 |             |                     |                 |
| HadoopSort         | 2020/3/31 | 15:30:29 | 35858           | 22.318      | 1606                | 1606            |
| HadoopWordcount    | 2020/3/31 | 15:34:12 | 36892           | 21.377      | 1725                | 1725            |
| HadoopTerasort     | 2020/3/31 | 15:48:45 | 3200000         | 21.441      | 149246              | 149246          |
| HadoopSleep        | 2020/3/31 | 15:49:52 | 0               | 21.495      | 0                   | 0               |
| HadoopDfsioe-read  | 2020/3/31 | 15:51:51 | 16869908        | 53.625      | 314590              | 314590          |
| HadoopDfsioe-write | 2020/3/31 | 15:52:52 | 16979420        | 55.921      | 303632              | 303632          |

### ZFM：157.111

| Type               | Date      | Time     | Input_data_size | Duration(s) | Throughput(bytes/s) | Throughput/node |
| ------------------ | --------- | -------- | --------------- | ----------- | ------------------- | --------------- |
| HadoopSort         | 2020/3/31 | 16:15:56 | 36425           | 21.412      | 1701                | 1701            |
| HadoopWordcount    | 2020/3/31 | 16:18:41 | 36204           | 21.542      | 1680                | 1680            |
| HadoopTerasort     | 2020/3/31 | 16:20:20 | 3200000         | 21.924      | 145958              | 145958          |
| HadoopSleep        | 2020/3/31 | 16:21:07 | 0               | 20.904      | 0                   | 0               |
| HadoopDfsioe-read  | 2020/3/31 | 16:25:45 | 16869908        | 51.72       | 326177              | 326177          |
| HadoopDfsioe-write | 2020/3/31 | 16:26:53 | 16978394        | 63.731      | 266407              | 266407          |

## 六、结论

1、在相同配置157.110和157.111两台服务器测试如上列举的用例1-用例5，所得hadoop的吞吐性能测试结果接近。

