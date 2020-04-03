#Spark性能对比测试

## 一、机器

参考[part1_硬件性能测试](./part1_硬件性能测试.md)

## 二、服务配置

相关配置文件见目录[spark配置文件](./files/spark/conf)

## 三、测试方案

采用HiBench测试框架，版本号：7.1-SNAPSHOT 2的改造版。

### HiBench的修改

为了支持spark 2.3版本，需要做如下修改

sparkbench/pom.xml

```xml
    <!-- support spark 2.3 @czw-->
    <profile>
      <id>spark2.3</id>
      <properties>
        <spark.version>2.3.0</spark.version>
        <spark.bin.version>2.3</spark.bin.version>
      </properties>
      <activation>
        <property>
          <name>spark</name>
          <value>2.3</value>
        </property>
      </activation>
    </profile>
```

sparkbench/streaming/pom.xml

```xml
    <!-- support spark 2.3 @czw-->  
    <profile>
      <id>spark2.3</id>
      <dependencies>
        <dependency>
          <groupId>org.apache.spark</groupId>
          <artifactId>spark-streaming-kafka-0-8_2.11</artifactId>
          <version>2.3.0</version>
        </dependency>
      </dependencies>
      <activation>
        <property>
          <name>spark</name>
          <value>2.3</value>
        </property>
      </activation>
    </profile>
```

sparkbench/structuredStreaming/pom.xml

```xml
    <!-- support spark 2.3 @czw-->
    <profile>
      <id>spark2.3</id>
      <dependencies>
        <dependency>
          <groupId>org.apache.spark</groupId>
          <artifactId>spark-streaming-kafka-0-8_${scala.binary.version}</artifactId>
          <version>2.3.0</version>
        </dependency>
        <dependency>
          <groupId>org.apache.spark</groupId>
          <artifactId>spark-sql-kafka-0-10_${scala.binary.version}</artifactId>
          <version>2.3.0</version>
        </dependency>
      </dependencies>
      <activation>
        <property>
          <name>spark</name>
          <value>2.3</value>
        </property>
      </activation>
    </profile>
```

编译

```shell
mvn  -Psparkbench -Dspark=2.3 -Dscala=2.11 clean package
```

### 遇到的错误与解决方法

1、报错

```
20/03/04 15:37:05 INFO zookeeper.ClientCnxn: EventThread shut down
Exception in thread "main" java.lang.NoSuchMethodError: kafka.admin.AdminUtils$.createTopic(Lorg/I0Itec/zkclient/ZkClient;Ljava/lang/String;IILjava/util/Properties;)V
        at com.intel.hibench.common.streaming.metrics.MetricsUtil$.createTopic(MetricsUtil.scala:39)
        at com.intel.hibench.sparkbench.streaming.RunBench$.main(RunBench.scala:66)
        at com.intel.hibench.sparkbench.streaming.RunBench.main(RunBench.scala)
        at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
        at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.lang.reflect.Method.invoke(Method.java:498)
        at org.apache.spark.deploy.JavaMainApplication.start(SparkApplication.scala:52)
```

解决思路：将kafka_2.11-0.8.2.1.jar 包放到spark集群上

```shell
[root@lv98-dct 0.8.2.1]# scp kafka_2.11-0.8.2.1.jar root@10.45.157.123://home/faraday/spark2/jars
kafka_2.11-0.8.2.1.jar                                                                                       100% 3862KB  73.3MB/s   00:00 
```

2、报错

```shell
Exception in thread "main" org.apache.hadoop.security.AccessControlException: Permission denied: user=root, access=WRITE, inode="/":hdfs:supergroup:drwxr-xr-x
```

root用户对根/目录无写权限，解决方法

```shell
sudo -u hdfs hadoop fs -chmod 777 /
```

3、报错

```
Exception in thread "main" java.lang.ClassCastException: kafka.cluster.Broker cannot be cast to kafka.cluster.BrokerEndPoint
        at org.apache.spark.streaming.kafka.KafkaCluster$$anonfun$2$$anonfun$3$$anonfun$apply$6$$anonfun$apply$7.apply(KafkaCluster.scala:98)
```

解决方法

```
spark-streaming-kafka-0-8_2.11-2.3.0.jar拷贝到/home/faraday/spark2/jars目录
```

4、报错

```
ERROR streaming.CheckpointWriter: Could not submit checkpoint task to the thread pool executor
java.util.concurrent.RejectedExecutionException: Task org.apache.spark.streaming.CheckpointWriter
```

参考：https://github.com/Intel-bigdata/HiBench/issues/416

> Hello,
>
> I think I found the cause.
> The datanode of my HDFS is running with a HDD which is very slow.
> It incured a long processing time for checkpointing.
>
> Fix method:
>
> 1. I tried to turn off checkpointing and it worked.
> 2. I tried to set "conf/spark.conf:hibench.streambench.spark.batchInterval" to a larger value. it worked.
>
> BR
> yong

修改conf/spark.conf文件

```shell
#修改前
# Spark streaming Batchnterval in millisecond (default 100)
hibench.streambench.spark.batchInterval          100
#修改后
hibench.streambench.spark.batchInterval          1000
```

### HiBench的配置

参见

目录[Hibench ZFM](./files/hibench/zfm/)

目录[Hibench CM](./files/hibench/cm/)

测试spark streaming时修改conf/hibench.conf文件，用例fixwindow



```shell
#======================================================
# Data generator for streaming benchmarks
#======================================================
# Interval span in millisecond (default: 50)
hibench.streambench.datagen.intervalSpan         50
# Number of records to generate per interval span (default: 5)
hibench.streambench.datagen.recordsPerInterval   100
# fixed length of record (default: 200)
hibench.streambench.datagen.recordLength         2000
# Number of KafkaProducer running on different thread (default: 1)
hibench.streambench.datagen.producerNumber       1
# Total round count of data send (default: -1 means infinity)
hibench.streambench.datagen.totalRounds          -1
# Number of total records that will be generated (default: -1 means infinity)
hibench.streambench.datagen.totalRecords        1800000
```



##四、测试用例

### 用例1：workload Sort

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/micro/sort/prepare/prepare.sh
[root@lv110 HiBench]# bin/workloads/micro/sort/spark/run.sh
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/micro/sort/prepare/prepare.sh
[root@lv111 HiBench]# bin/workloads/micro/sort/spark/run.sh
```



### 用例2：workload TeraSort

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/micro/terasort/prepare/prepare.sh
[root@lv110 HiBench]# bin/workloads/micro/terasort/spark/run.sh 
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/micro/terasort/prepare/prepare.sh
[root@lv111 HiBench]# bin/workloads/micro/terasort/spark/run.sh
```



### 用例3： workload WordCount

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/micro/wordcount/prepare/prepare.sh 
[root@lv110 HiBench]# bin/workloads/micro/terasort/spark/run.sh
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/micro/wordcount/prepare/prepare.sh
[root@lv111 HiBench]# bin/workloads/micro/wordcount/spark/run.sh
```



### 用例4：workload SQL Scan

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/sql/scan/prepare/prepare.sh 
[root@lv110 HiBench]# bin/workloads/sql/scan/spark/run.sh
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/sql/scan/prepare/prepare.sh
[root@lv111 HiBench]# bin/workloads/sql/scan/spark/run.sh 
```



### 用例5：workload SQL Join

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/sql/join/prepare/prepare.sh
[root@lv110 HiBench]# bin/workloads/sql/join/spark/run.sh 
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/sql/join/prepare/prepare.sh 
[root@lv111 HiBench]# bin/workloads/sql/join/spark/run.sh 
```



### 用例6：workload SQL Aggregation

CM：157.110

```shell
[root@lv110 HiBench]# bin/workloads/sql/aggregation/prepare/prepare.sh
[root@lv110 HiBench]# bin/workloads/sql/aggregation/spark/run.sh 
```

ZFM：157.111

```shell
[root@lv111 HiBench]# bin/workloads/sql/aggregation/prepare/prepare.sh 
[root@lv111 HiBench]# bin/workloads/sql/aggregation/spark/run.sh 
```



### 用例7：workload Streaming Identity

CM：157.110

```shell
#数据
[root@lv110 HiBench]# bin/workloads/streaming/identity/prepare/genSeedDataset.sh
[root@lv110 HiBench]# bin/workloads/streaming/identity/prepare/dataGen.sh
#运行
[root@lv110 HiBench]# bin/workloads/streaming/identity/spark/run.sh 

#Reporter Topic: SPARK_identity_1_100_50_1585891601618
#生成报告
[root@lv110 HiBench]# bin/workloads/streaming/identity/common/metrics_reader.sh 
#SPARK_identity_1_100_50_1585891601618.csv
```

ZFM：157.111

```shell
#数据
[root@lv111 HiBench]# bin/workloads/streaming/identity/prepare/genSeedDataset.sh
[root@lv111 HiBench]# bin/workloads/streaming/identity/prepare/dataGen.sh
#运行
[root@lv111 HiBench]# bin/workloads/streaming/identity/spark/run.sh 

#Reporter Topic: SPARK_identity_1_100_50_1585891612766
#生成报告
[root@lv111 HiBench]# bin/workloads/streaming/identity/common/metrics_reader.sh 
#SPARK_identity_1_100_50_1585891612766.csv
```



### 用例8：workload Streaming Repartition

CM：157.110

```shell
#数据
[root@lv110 HiBench]# bin/workloads/streaming/repartition/prepare/genSeedDataset.sh 
[root@lv110 HiBench]# bin/workloads/streaming/repartition/prepare/dataGen.sh 
#运行
[root@lv110 HiBench]# bin/workloads/streaming/repartition/spark/run.sh 
#Reporter Topic: SPARK_repartition_1_100_50_1585893239448
#生成报告
[root@lv110 HiBench]# bin/workloads/streaming/repartition/common/metrics_reader.sh 
#SPARK_repartition_1_100_50_1585893239448.csv
```

ZFM：157.111

```shell
#数据
[root@lv111 HiBench]# bin/workloads/streaming/repartition/prepare/genSeedDataset.sh 
[root@lv111 HiBench]# bin/workloads/streaming/repartition/prepare/dataGen.sh 
#运行
[root@lv111 HiBench]# bin/workloads/streaming/repartition/spark/run.sh 
#Reporter Topic: SPARK_repartition_1_100_50_1585893245265
#生成报告
[root@lv111 HiBench]# bin/workloads/streaming/repartition/common/metrics_reader.sh
#SPARK_repartition_1_100_50_1585893245265.csv
```



### 用例9：workload Streaming Stateful Wordcount

CM：157.110

```shell
#数据
[root@lv110 HiBench]# bin/workloads/streaming/wordcount/prepare/genSeedDataset.sh
[root@lv110 HiBench]# bin/workloads/streaming/wordcount/prepare/dataGen.sh 
#运行
[root@lv110 HiBench]# bin/workloads/streaming/identity/spark/run.sh 
#Reporter Topic: SPARK_wordcount_1_100_50_1585897616580
#生成报告
[root@lv110 HiBench]#  bin/workloads/streaming/wordcount/common/metrics_reader.sh 
#SPARK_wordcount_1_100_50_1585897616580.csv
```

ZFM：157.111

```shell
#数据
[root@lv111 HiBench]# bin/workloads/streaming/wordcount/prepare/genSeedDataset.sh
[root@lv111 HiBench]# bin/workloads/streaming/wordcount/prepare/dataGen.sh 
#运行
[root@lv111 HiBench]# bin/workloads/streaming/repartition/spark/run.sh
#Reporter Topic: SPARK_wordcount_1_100_50_1585897622145
#生成报告
[root@lv111 HiBench]# bin/workloads/streaming/wordcount/common/metrics_reader.sh
#SPARK_wordcount_1_100_50_1585897622145.csv
```



### 用例10：workload Streaming Fixwindow

CM：157.110

```shell
#数据
[root@lv110 HiBench]#  bin/workloads/streaming/fixwindow/prepare/genSeedDataset.sh 
[root@lv110 HiBench]#  bin/workloads/streaming/fixwindow/prepare/dataGen.sh
#运行
[root@lv110 HiBench]# bin/workloads/streaming/fixwindow/spark/run.sh 
Reporter Topic: SPARK_fixwindow_1_100_50_1585899322228
#生成报告
[root@lv110 HiBench]# bin/workloads/streaming/fixwindow/common/metrics_reader.sh
#SPARK_fixwindow_1_100_50_1585899322228.csv
```

ZFM：157.111

```shell
#数据
[root@lv111 HiBench]# bin/workloads/streaming/fixwindow/prepare/genSeedDataset.sh
[root@lv111 HiBench]# bin/workloads/streaming/fixwindow/prepare/dataGen.sh
#运行
[root@lv111 HiBench]# bin/workloads/streaming/fixwindow/spark/run.sh 
#Reporter Topic: SPARK_fixwindow_1_100_50_1585899327478
#生成报告
[root@lv111 HiBench]# bin/workloads/streaming/fixwindow/common/metrics_reader.sh
#SPARK_fixwindow_1_100_50_1585899327478.csv
```



## 五、测试结果

### CM：157.110

| Type                  | Date     | Time     | Input_data_size | Duration(s) | Throughput(bytes/s) | Throughput/node |
| --------------------- | -------- | -------- | --------------- | ----------- | ------------------- | --------------- |
| ScalaSparkSort        | 2020/4/1 | 13:32:13 | 36661           | 22.473      | 1631                | 1631            |
| ScalaSparkTerasort    | 2020/4/1 | 15:49:55 | 3200000         | 21.403      | 149511              | 149511          |
| ScalaSparkWordcount   | 2020/4/1 | 16:11:18 | 36111           | 21.305      | 1694                | 1694            |
| ScalaSparkScan        | 2020/4/1 | 16:15:41 | 206231          | 32.789      | 6289                | 6289            |
| ScalaSparkJoin        | 2020/4/1 | 16:20:54 | 199243          | 43.23       | 4608                | 4608            |
| ScalaSparkAggregation | 2020/4/1 | 16:29:40 | 37988           | 32.389      | 1172                | 1172            |

|                     | time                         | count   | throughput(msgs/s) | max_latency(ms) | mean_latency(ms) | min_latency(ms) | stddev_latency(ms) | p50_latency(ms) | p75_latency(ms) | p95_latency(ms) | p98_latency(ms) | p99_latency(ms) | p999_latency(ms) |
| ------------------- | ---------------------------- | ------- | ------------------ | --------------- | ---------------- | --------------- | ------------------ | --------------- | --------------- | --------------- | --------------- | --------------- | ---------------- |
| identity_157.110    | Fri Apr 03 13:45:15 CST 2020 | 1772400 | 1998               | 2821            | 517.545          | 22              | 297.387            | 526             | 776             | 976             | 984             | 1014            | 2041             |
| repartition_157.110 | Fri Apr 03 14:41:08 CST 2020 | 1771800 | 1998               | 3542            | 586.286          | 65              | 310.056            | 583             | 833             | 1033            | 1078            | 1153            | 2652             |
| wordcount_157.110   | Fri Apr 03 15:29:22 CST 2020 | 1774100 | 1997               | 3480            | 645.963          | 72              | 345.799            | 641             | 896             | 1136            | 1405            | 1648            | 2618             |
| fixwindow_157.110   | Fri Apr 03 15:53:22 CST 2020 | 1771300 | 1990               | 12156           | 5495.568         | 414             | 2889.903           | 5504            | 7992            | 9983            | 10282           | 10382           | 11305            |

### ZFM：157.111

| Type                  | Date     | Time     | Input_data_size | Duration(s) | Throughput(bytes/s) | Throughput/node |
| --------------------- | -------- | -------- | --------------- | ----------- | ------------------- | --------------- |
| ScalaSparkSort        | 2020/4/1 | 15:26:06 | 35949           | 20.395      | 1762                | 1762            |
| ScalaSparkTerasort    | 2020/4/1 | 15:50:19 | 3200000         | 21.73       | 147261              | 147261          |
| ScalaSparkWordcount   | 2020/4/1 | 16:12:01 | 36379           | 20.395      | 1783                | 1783            |
| ScalaSparkScan        | 2020/4/1 | 16:17:54 | 206231          | 31.215      | 6606                | 6606            |
| ScalaSparkJoin        | 2020/4/1 | 16:25:27 | 199243          | 39.106      | 5094                | 5094            |
| ScalaSparkAggregation | 2020/4/1 | 16:30:05 | 37988           | 31.946      | 1189                | 1189            |

|                     | time                         | count   | throughput(msgs/s) | max_latency(ms) | mean_latency(ms) | min_latency(ms) | stddev_latency(ms) | p50_latency(ms) | p75_latency(ms) | p95_latency(ms) | p98_latency(ms) | p99_latency(ms) | p999_latency(ms) |
| ------------------- | ---------------------------- | ------- | ------------------ | --------------- | ---------------- | --------------- | ------------------ | --------------- | --------------- | --------------- | --------------- | --------------- | ---------------- |
| identity_157.111    | Fri Apr 03 13:45:34 CST 2020 | 1772200 | 1999               | 6608            | 547.417          | 21              | 458.962            | 528             | 778             | 978             | 994             | 1903            | 5709             |
| repartition_157.111 | Fri Apr 03 14:41:57 CST 2020 | 1774500 | 1998               | 8315            | 663.469          | 89              | 581.148            | 609             | 862             | 1065            | 1236            | 3184            | 7406             |
| wordcount_157.111   | Fri Apr 03 15:30:46 CST 2020 | 1774800 | 1998               | 11061           | 769.673          | 73              | 1002.449           | 638             | 894             | 1243            | 3721.6          | 6585            | 10366            |
| fixwindow_157.111   | Fri Apr 03 15:53:34 CST 2020 | 1775800 | 1993               | 18435           | 5643.922         | 392             | 3079.569           | 5604            | 8137            | 10135           | 10448           | 13079           | 17578            |

## 六、结论

1、用例1-6的测试结果表明，spark core和spark sql的吞吐性能指标是接近的。

2、

