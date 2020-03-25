# Kafka性能测试

## 一、机器

参考[part1_测试环境](./part1_测试环境.md)

## 二、服务配置

### server.properties

```properties
auto.create.topics.enable=true
auto.leader.rebalance.enable=true
broker.id=25
controlled.shutdown.enable=true
controlled.shutdown.max.retries=3
default.replication.factor=1
delete.topic.enable=true
kafka.http.metrics.host=0.0.0.0
kafka.http.metrics.port=24042
kafka.log4j.dir=/disk1/log/kafka
kerberos.auth.enable=false
leader.imbalance.check.interval.seconds=300
leader.imbalance.per.broker.percentage=10
log.cleaner.dedupe.buffer.size=134217728
log.cleaner.delete.retention.ms=604800000
log.cleaner.enable=true
log.cleaner.min.cleanable.ratio=0.5
log.cleaner.threads=1
log.dirs=/disk1/data/kafka,/disk2/data/kafka,/disk3/data/kafka,/disk4/data/kafka,/disk5/data/kafka,/disk6/data/kafka
log.retention.bytes=-1
log.retention.check.interval.ms=300000
log.retention.hours=720
log.roll.hours=168
log.segment.bytes=1073741824
message.max.bytes=1000000
min.insync.replicas=1
num.io.threads=8
num.partitions=10
num.replica.fetchers=1
offsets.topic.num.partitions=50
offsets.topic.replication.factor=1
port=9092
replica.fetch.max.bytes=1048576
replica.lag.max.messages=4000
replica.lag.time.max.ms=10000
sentry.kafka.caching.enable=true
sentry.kafka.caching.ttl.ms=30000
sentry.kafka.caching.update.failures.count=3
unclean.leader.election.enable=false
zookeeper.session.timeout.ms=6000
zookeeper.connect=lv111.dct-znv.com:2181
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter
security.inter.broker.protocol=PLAINTEXT
listeners=PLAINTEXT://lv111.dct-znv.com:9092,
broker.id.generation.enable=false
sasl.kerberos.service.name=kafka
```

consumer.properties和producer.properties都用的默认

##三、测试方案

###kafka 0.8.x版本

```shell
#Producer

##Setup
bin/kafka-topics.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --create --topic test-rep-one --partitions 6 --replication-factor 1
bin/kafka-topics.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --create --topic test --partitions 6 --replication-factor 3

##Single thread, no replication

bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test7 50000000 100 -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=8196

##Single-thread, async 3x replication

bin/kafktopics.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --create --topic test --partitions 6 --replication-factor 3
bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test6 50000000 100 -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=8196

##Single-thread, sync 3x replication

bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test 50000000 100 -1 acks=-1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=64000

##Three Producers, 3x async replication
bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test 50000000 100 -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=8196

##Throughput Versus Stored Data

bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test 50000000000 100 -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=8196

##Effect of message size

for i in 10 100 1000 10000 100000;
do
echo ""
echo $i
bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test $((1000*1024*1024/$i)) $i -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=128000
done;

#Consumer
##Consumer throughput

bin/kafka-consumer-perf-test.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --messages 50000000 --topic test --threads 1

##3 Consumers

On three servers, run:
bin/kafka-consumer-perf-test.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --messages 50000000 --topic test --threads 1

#End-to-end Latency

bin/kafka-run-class.sh kafka.tools.TestEndToEndLatency esv4-hcl198.grid.linkedin.com:9092 esv4-hcl197.grid.linkedin.com:2181 test 5000

#Producer and consumer

bin/kafka-run-class.sh org.apache.kafka.clients.tools.ProducerPerformance test 50000000 100 -1 acks=1 bootstrap.servers=esv4-hcl198.grid.linkedin.com:9092 buffer.memory=67108864 batch.size=8196

bin/kafka-consumer-perf-test.sh --zookeeper esv4-hcl197.grid.linkedin.com:2181 --messages 50000000 --topic test --threads 1

```

###Kafka 1.0.0版本

```shell
#Producer

##Setup
bin/kafka-topics.sh --zookeeper localhost:2181/kafka-local --create --topic test-rep-one --partitions 6 --replication-factor 1
bin/kafka-topics.sh --zookeeper localhost:2181/kafka-local --create --topic test-rep-two --partitions 6 --replication-factor 3

##Single thread, no replication
bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=kafka_host:9092 buffer.memory=67108864 batch.size=8196

##Single-thread, async 3x replication
bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-two --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=kafka_host:9092 acks=1 buffer.memory=67108864 batch.size=8196

##Single-thread, sync 3x replication
bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-two --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=kafka_host:9092 acks=-1 buffer.memory=67108864 batch.size=8196

##Effect of message size

for i in 10 100 1000 10000 100000;
do
echo ""
echo $i
bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-two --num-records  $((1000*1024*1024/$i)) --throughput 100000 --record-size $i --producer-props bootstrap.servers=kafka_host:9092 acks=1 buffer.memory=67108864 batch.size=8196
done;


#Consumer

##Consumer throughput
kafka-consumer-perf-test --broker-list kafka_host:9092 --messages 6000000 --threads 1 --topic test-rep-two --print-metrics

##3 Consumers

##On three servers, run:
kafka-consumer-perf-test --broker-list kafka_host:9092 --messages 6000000 --threads 1 --topic test-rep-two --print-metrics

```

### 删除kafka topic

> 1、删除kafka存储目录（server.properties文件log.dirs配置，默认为"/tmp/kafka-logs"）相关topic目录
>  2、Kafka 删除topic的命令是：
>
> 
>
> ```cpp
>    ./bin/kafka-topics  --delete --zookeeper 【zookeeper server】  --topic 【topic name】
> ```
>
> 如果kafaka启动时加载的配置文件中server.properties没有配置delete.topic.enable=true，那么此时的删除并不是真正的删除，而是把topic标记为：marked for deletion
>  你可以通过命令：
>
> 
>
> ```cpp
> ./bin/kafka-topics --zookeeper 【zookeeper server】 --list 
> ```
>
> 来查看所有topic
>
> 此时你若想真正删除它，可以登录zookeeper客户端：
>  命令：
>
> 
>
> ```undefined
> ./bin/zookeeper-client
> ```
>
> 找到topic所在的目录：
>
> 
>
> ```undefined
> ls /brokers/topics
> ```
>
> 找到要删除的topic，执行命令：
>
> 
>
> ```undefined
> rmr /brokers/topics/【topic name】
> ```
>
> 即可，此时topic被彻底删除
>  另外被标记为marked for deletion的topic你可以在zookeeper客户端中通过命令获得：
>
> 
>
> ```undefined
> ls /admin/delete_topics/【topic name】
> ```
>
> 如果你删除了此处的topic，那么marked for deletion 标记消失
>  zookeeper 的config中也有有关topic的信息：
>
> 
>
> ```undefined
>  ls /config/topics/【topic name】
> ```
>
> 暂时不知道有什么用
>
> 总结：
>  彻底删除topic：
>  1、删除kafka存储目录（server.properties文件log.dirs配置，默认为"/tmp/kafka-logs"）相关topic目录
>  2、如果配置了delete.topic.enable=true直接通过命令删除，如果命令删除不掉，直接通过zookeeper-client 删除掉broker下的topic即可。
>
> https://blog.csdn.net/fengzheku/article/details/50585972

## 四、测试结果

### 用例1：单borker，生产者，单线程，六分区，无副本，消息payload 100字节

#### CM：157.110

```shell
#创建topic
[root@lv110 KAFKA]# pwd
/opt/cloudera/parcels/KAFKA
[root@lv110 KAFKA]# bin/kafka-topics --zookeeper 10.45.157.110:2181 --create --topic test-rep-one --partitions 6 --replication-factor 1

```

```shell
#单线程，无副本情况
[root@lv110 KAFKA]# bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=10.45.157.110:9092 buffer.memory=67108864 batch.size=8196
```

测试结果

```
499856 records sent, 99971.2 records/sec (9.53 MB/sec), 33.1 ms avg latency, 416.0 max latency.
501246 records sent, 100249.2 records/sec (9.56 MB/sec), 1.1 ms avg latency, 28.0 max latency.
500100 records sent, 100020.0 records/sec (9.54 MB/sec), 1.1 ms avg latency, 21.0 max latency.
500100 records sent, 100020.0 records/sec (9.54 MB/sec), 1.2 ms avg latency, 21.0 max latency.
500113 records sent, 100022.6 records/sec (9.54 MB/sec), 1.1 ms avg latency, 16.0 max latency.
500187 records sent, 100017.4 records/sec (9.54 MB/sec), 1.0 ms avg latency, 14.0 max latency.
500180 records sent, 100036.0 records/sec (9.54 MB/sec), 1.1 ms avg latency, 23.0 max latency.
500020 records sent, 100004.0 records/sec (9.54 MB/sec), 1.1 ms avg latency, 18.0 max latency.
500100 records sent, 100020.0 records/sec (9.54 MB/sec), 1.0 ms avg latency, 12.0 max latency.
500100 records sent, 100020.0 records/sec (9.54 MB/sec), 1.1 ms avg latency, 29.0 max latency.
500072 records sent, 100014.4 records/sec (9.54 MB/sec), 1.1 ms avg latency, 25.0 max latency.
6000000 records sent, 99998.333361 records/sec (9.54 MB/sec), 3.76 ms avg latency, 416.00 ms max latency, 1 ms 50th, 2 ms 95th, 72 ms 99th, 344 ms 99.9th.

```

<details> 
<summary>其他指标，展开查看</summary> 
<pre><code> 
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 1115.149
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8137.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.000
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 0.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 362831.105
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 21766238.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.070
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 16263.045
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.774
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 180573.994
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 46024198498.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 4153495932.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 59.975
producer-metrics:network-io-rate:{client-id=producer-1}                              : 3655.623
producer-metrics:network-io-total:{client-id=producer-1}                             : 724269735.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 11730456.451
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 702503497.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 0.410
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 352.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 100126.827
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 186.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 186.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 57.093
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 0.979
producer-metrics:request-latency-max:{client-id=producer-1}                          : 319.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 1827.839
producer-metrics:request-size-avg:{client-id=producer-1}                             : 6417.664
producer-metrics:request-size-max:{client-id=producer-1}                             : 48924.000
producer-metrics:request-total:{client-id=producer-1}                                : 702503497.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 1751.846
producer-metrics:response-total:{client-id=producer-1}                               : 21766238.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 4286.628
producer-metrics:select-total:{client-id=producer-1}                                 : 46024198498.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 8.601
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 363185.750
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 21765722.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 11721870.651
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 702503430.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 0.979
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 319.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 1753.567
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 6684.588
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 48924.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 702503430.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.033
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 1753.596
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 21765722.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 11546094.022
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 691865046.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 100130.169
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
20/03/24 11:27:49 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms. 
</code></pre> 
</details>

#### ZFM：157.111

```shell
#创建topic
[root@lv111 kafka]# pwd
/home/faraday/kafka
[root@lv111 kafka]#  bin/kafka-topics.sh --zookeeper 10.45.157.111:2181 --create --topic test-rep-one --partitions 6 --replication-factor 1
```

```shell
#单线程，无副本情况
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=10.45.157.111:9092 buffer.memory=67108864 batch.size=8196
```

测试结果

```
499802 records sent, 99960.4 records/sec (9.53 MB/sec), 33.4 ms avg latency, 454.0 max latency.
500700 records sent, 100140.0 records/sec (9.55 MB/sec), 1.4 ms avg latency, 40.0 max latency.
500128 records sent, 100025.6 records/sec (9.54 MB/sec), 1.1 ms avg latency, 14.0 max latency.
499993 records sent, 99998.6 records/sec (9.54 MB/sec), 1.0 ms avg latency, 16.0 max latency.
500231 records sent, 100046.2 records/sec (9.54 MB/sec), 1.6 ms avg latency, 31.0 max latency.
500148 records sent, 100009.6 records/sec (9.54 MB/sec), 1.2 ms avg latency, 17.0 max latency.
500082 records sent, 100016.4 records/sec (9.54 MB/sec), 1.7 ms avg latency, 46.0 max latency.
500117 records sent, 100023.4 records/sec (9.54 MB/sec), 1.4 ms avg latency, 41.0 max latency.
499957 records sent, 99991.4 records/sec (9.54 MB/sec), 1.2 ms avg latency, 15.0 max latency.
500154 records sent, 100030.8 records/sec (9.54 MB/sec), 1.2 ms avg latency, 17.0 max latency.
499986 records sent, 99997.2 records/sec (9.54 MB/sec), 1.3 ms avg latency, 19.0 max latency.
6000000 records sent, 99998.333361 records/sec (9.54 MB/sec), 3.98 ms avg latency, 454.00 ms max latency, 1 ms 50th, 2 ms 95th, 132 ms 99th, 279 ms 99.9th.


```

<details>
<summary>其他指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 1103.183
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8137.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.000
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 0.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 367817.924
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 22031558.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.067
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 15204.807
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.774
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 175286.510
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 46320191273.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 3967447060.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 59.872
producer-metrics:network-io-rate:{client-id=producer-1}                              : 3566.020
producer-metrics:network-io-total:{client-id=producer-1}                             : 725122185.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 11736956.247
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 703090627.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 0.424
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 273.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 100269.055
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 186.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 186.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 56.175
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 1.110
producer-metrics:request-latency-max:{client-id=producer-1}                          : 267.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 1783.070
producer-metrics:request-size-avg:{client-id=producer-1}                             : 6582.444
producer-metrics:request-size-max:{client-id=producer-1}                             : 48924.000
producer-metrics:request-total:{client-id=producer-1}                                : 703090627.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 1783.218
producer-metrics:response-total:{client-id=producer-1}                               : 22031558.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 4415.862
producer-metrics:select-total:{client-id=producer-1}                                 : 46320191273.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 8.614
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 368147.352
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 22031042.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 1.118
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 11748526.360
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 703090560.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 1.110
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 267.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.033
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 1784.794
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 33.500
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 6582.567
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : 43.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 48924.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 703090560.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.033
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 1784.854
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 22031042.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 11569804.569
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 692302396.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 100270.731
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```

### 用例2：单broker，生产者，单线程，六分区，异步，消息payload 10字节

#### CM: 157.110

```shell

#生产者
[root@lv110 KAFKA]# bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 10 --producer-props bootstrap.servers=10.45.157.110:9092 acks=1 buffer.memory=67108864 batch.size=8196

```

测试结果

```
499878 records sent, 99955.6 records/sec (0.95 MB/sec), 0.9 ms avg latency, 61.0 max latency.
500518 records sent, 100103.6 records/sec (0.95 MB/sec), 1.1 ms avg latency, 21.0 max latency.
500005 records sent, 100001.0 records/sec (0.95 MB/sec), 1.0 ms avg latency, 15.0 max latency.
500063 records sent, 100012.6 records/sec (0.95 MB/sec), 1.2 ms avg latency, 25.0 max latency.
500196 records sent, 100039.2 records/sec (0.95 MB/sec), 1.0 ms avg latency, 17.0 max latency.
499942 records sent, 99988.4 records/sec (0.95 MB/sec), 1.5 ms avg latency, 50.0 max latency.
500200 records sent, 100020.0 records/sec (0.95 MB/sec), 0.9 ms avg latency, 16.0 max latency.
500194 records sent, 100038.8 records/sec (0.95 MB/sec), 1.1 ms avg latency, 42.0 max latency.
499872 records sent, 99974.4 records/sec (0.95 MB/sec), 1.1 ms avg latency, 20.0 max latency.
500098 records sent, 100019.6 records/sec (0.95 MB/sec), 0.9 ms avg latency, 14.0 max latency.
500012 records sent, 100002.4 records/sec (0.95 MB/sec), 0.9 ms avg latency, 11.0 max latency.
6000000 records sent, 99998.333361 records/sec (0.95 MB/sec), 1.05 ms avg latency, 61.00 ms max latency, 1 ms 50th, 2 ms 95th, 8 ms 99th, 27 ms 99.9th.
```

<details>
<summary>其他指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 206.059
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8187.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.000
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 0.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 418005.000
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 24695318.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.068
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 15230.665
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.797
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 179655.632
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 47579508343.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 4069497191.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 59.998
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4050.895
producer-metrics:network-io-total:{client-id=producer-1}                             : 181756834.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 2630608.480
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 157061516.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 0.060
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 40.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 100051.693
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 95.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 95.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 50.171
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 0.867
producer-metrics:request-latency-max:{client-id=producer-1}                          : 50.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2025.532
producer-metrics:request-size-avg:{client-id=producer-1}                             : 1298.724
producer-metrics:request-size-max:{client-id=producer-1}                             : 49224.000
producer-metrics:request-total:{client-id=producer-1}                                : 157061516.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2025.567
producer-metrics:response-total:{client-id=producer-1}                               : 24695318.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 4437.109
producer-metrics:select-total:{client-id=producer-1}                                 : 47579508343.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 411765.328
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 24694802.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 2618869.308
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 157061449.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 0.867
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 50.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 1994.064
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 1313.311
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 49224.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 157061449.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 1994.097
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 24694802.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 2417580.052
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 144975023.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 100051.693
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
20/03/24 14:38:05 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms.
</code></pre>
</details>



#### ZFM:157.111

```shell
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 10 --producer-props bootstrap.servers=10.45.157.111:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

```
499802 records sent, 99960.4 records/sec (0.95 MB/sec), 1.7 ms avg latency, 162.0 max latency.
500050 records sent, 99830.3 records/sec (0.95 MB/sec), 1.4 ms avg latency, 32.0 max latency.
500568 records sent, 99814.2 records/sec (0.95 MB/sec), 1.4 ms avg latency, 52.0 max latency.
502382 records sent, 100476.4 records/sec (0.96 MB/sec), 1.6 ms avg latency, 68.0 max latency.
500044 records sent, 100008.8 records/sec (0.95 MB/sec), 1.1 ms avg latency, 21.0 max latency.
494256 records sent, 98634.2 records/sec (0.94 MB/sec), 1.1 ms avg latency, 69.0 max latency.
506900 records sent, 101177.6 records/sec (0.96 MB/sec), 1.7 ms avg latency, 78.0 max latency.
496000 records sent, 99200.0 records/sec (0.95 MB/sec), 1.1 ms avg latency, 52.0 max latency.
505200 records sent, 101040.0 records/sec (0.96 MB/sec), 1.4 ms avg latency, 53.0 max latency.
496608 records sent, 99301.7 records/sec (0.95 MB/sec), 1.2 ms avg latency, 38.0 max latency.
503694 records sent, 100738.8 records/sec (0.96 MB/sec), 1.4 ms avg latency, 54.0 max latency.
488514 records sent, 97663.7 records/sec (0.93 MB/sec), 1.1 ms avg latency, 120.0 max latency.
6000000 records sent, 99843.578394 records/sec (0.95 MB/sec), 1.46 ms avg latency, 162.00 ms max latency, 1 ms 50th, 2 ms 95th, 14 ms 99th, 81 ms 99.9th.
```

<details>
<summary>其他指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 204.575
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8187.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.000
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 0.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 416293.263
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 24975098.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.071
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 15536.645
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.793
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 174575.152
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 47286235900.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 4234649126.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 59.990
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4046.567
producer-metrics:network-io-total:{client-id=producer-1}                             : 182689435.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 2628703.719
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 157714337.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 0.066
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 45.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 100065.042
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 95.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 95.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 49.427
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 0.999
producer-metrics:request-latency-max:{client-id=producer-1}                          : 136.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2023.351
producer-metrics:request-size-avg:{client-id=producer-1}                             : 1299.183
producer-metrics:request-size-max:{client-id=producer-1}                             : 49224.000
producer-metrics:request-total:{client-id=producer-1}                                : 157714337.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2023.419
producer-metrics:response-total:{client-id=producer-1}                               : 24975098.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 4542.970
producer-metrics:select-total:{client-id=producer-1}                                 : 47286235900.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 8.601
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 416485.983
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 24974582.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 1.117
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 2630105.395
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 157714270.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 0.999
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 136.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.033
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 2024.398
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 33.500
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 1299.204
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : 43.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 49224.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 157714270.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.033
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 2024.398
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 24974582.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 2426123.916
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 145470390.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 100065.042
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```



### 用例3：单broker，生产者，单线程，六分区，异步，消息payload 1000字节

#### CM：157.110

```shell
[root@lv110 KAFKA]#  bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 1000 --producer-props bootstrap.servers=10.45.157.110:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
499221 records sent, 99844.2 records/sec (95.22 MB/sec), 41.5 ms avg latency, 145.0 max latency.
500737 records sent, 100147.4 records/sec (95.51 MB/sec), 9.8 ms avg latency, 57.0 max latency.
466671 records sent, 93334.2 records/sec (89.01 MB/sec), 121.3 ms avg latency, 339.0 max latency.
506976 records sent, 101395.2 records/sec (96.70 MB/sec), 370.2 ms avg latency, 436.0 max latency.
485184 records sent, 97036.8 records/sec (92.54 MB/sec), 352.0 ms avg latency, 553.0 max latency.
365808 records sent, 73161.6 records/sec (69.77 MB/sec), 749.3 ms avg latency, 1540.0 max latency.
659088 records sent, 131817.6 records/sec (125.71 MB/sec), 354.1 ms avg latency, 701.0 max latency.
491184 records sent, 98236.8 records/sec (93.69 MB/sec), 136.3 ms avg latency, 258.0 max latency.
481392 records sent, 96278.4 records/sec (91.82 MB/sec), 390.4 ms avg latency, 505.0 max latency.
480720 records sent, 96144.0 records/sec (91.69 MB/sec), 380.6 ms avg latency, 637.0 max latency.
546000 records sent, 109200.0 records/sec (104.14 MB/sec), 405.6 ms avg latency, 717.0 max latency.
501029 records sent, 100205.8 records/sec (95.56 MB/sec), 75.1 ms avg latency, 178.0 max latency.
6000000 records sent, 99715.809942 records/sec (95.10 MB/sec), 274.65 ms avg latency, 1540.00 ms max latency, 275 ms 50th, 675 ms 95th, 1276 ms 99th, 1321 ms 99.9th.
```

<details>
<summary>展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 8081.383
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8133.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.143
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 4828612766.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 462539.152
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 26650238.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.086
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 3285.518
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.619
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 23519.048
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 37514928018.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5120140328.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 60.198
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4409.025
producer-metrics:network-io-total:{client-id=producer-1}                             : 6140036713.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 107006218.613
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6113386475.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 288.863
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 715.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 105000.696
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 1086.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 1086.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 47.641
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.239
producer-metrics:request-latency-max:{client-id=producer-1}                          : 54.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2204.503
producer-metrics:request-size-avg:{client-id=producer-1}                             : 48538.241
producer-metrics:request-size-max:{client-id=producer-1}                             : 48900.000
producer-metrics:request-total:{client-id=producer-1}                                : 6113386475.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2204.615
producer-metrics:response-total:{client-id=producer-1}                               : 26650238.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 26318.095
producer-metrics:select-total:{client-id=producer-1}                                 : 37514928018.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 462450.691
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 26649722.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 106978606.656
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 6113386408.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 2.239
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 54.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 2204.031
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 48537.707
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 48900.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 6113386408.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 2204.197
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 26649722.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 106750474.550
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6100429898.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 104996.220
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
20/03/24 14:51:58 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms.
</code></pre>
</details>

#### ZFM：157.111

```shell
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 1000 --producer-props bootstrap.servers=10.45.157.111:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
473249 records sent, 94649.8 records/sec (90.27 MB/sec), 410.6 ms avg latency, 562.0 max latency.
483072 records sent, 96614.4 records/sec (92.14 MB/sec), 218.9 ms avg latency, 439.0 max latency.
510672 records sent, 102134.4 records/sec (97.40 MB/sec), 500.9 ms avg latency, 622.0 max latency.
511721 records sent, 102344.2 records/sec (97.60 MB/sec), 107.9 ms avg latency, 334.0 max latency.
417120 records sent, 83424.0 records/sec (79.56 MB/sec), 582.3 ms avg latency, 990.0 max latency.
604279 records sent, 120855.8 records/sec (115.26 MB/sec), 203.5 ms avg latency, 829.0 max latency.
499542 records sent, 99908.4 records/sec (95.28 MB/sec), 29.6 ms avg latency, 246.0 max latency.
466338 records sent, 93118.6 records/sec (88.80 MB/sec), 141.4 ms avg latency, 353.0 max latency.
535307 records sent, 107061.4 records/sec (102.10 MB/sec), 216.7 ms avg latency, 481.0 max latency.
500015 records sent, 100003.0 records/sec (95.37 MB/sec), 34.8 ms avg latency, 138.0 max latency.
401666 records sent, 80333.2 records/sec (76.61 MB/sec), 184.8 ms avg latency, 988.0 max latency.
496128 records sent, 99225.6 records/sec (94.63 MB/sec), 692.4 ms avg latency, 1044.0 max latency.
6000000 records sent, 98706.939098 records/sec (94.13 MB/sec), 276.68 ms avg latency, 1044.00 ms max latency, 223 ms 50th, 762 ms 95th, 987 ms 99th, 1021 ms 99.9th.
```

<details>
<summary>其他指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 7767.177
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8140.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.182
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 7067238742.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 446404.571
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 27190058.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.095
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 3202.790
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.600
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 20206.212
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 35656104169.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5838330545.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 60.710
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4283.101
producer-metrics:network-io-total:{client-id=producer-1}                             : 6141773394.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 99145097.929
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6114583336.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 216.615
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 1041.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 97271.806
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 1086.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 1086.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 45.431
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.144
producer-metrics:request-latency-max:{client-id=producer-1}                          : 483.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2141.587
producer-metrics:request-size-avg:{client-id=producer-1}                             : 46295.143
producer-metrics:request-size-max:{client-id=producer-1}                             : 48935.000
producer-metrics:request-total:{client-id=producer-1}                                : 6114583336.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2141.564
producer-metrics:response-total:{client-id=producer-1}                               : 27190058.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 29689.194
producer-metrics:select-total:{client-id=producer-1}                                 : 35656104169.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 446327.847
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 27189542.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 99142140.851
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 6114583269.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 2.144
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 483.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 2141.074
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 46303.353
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 48935.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 6114583269.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 2141.144
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 27189542.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 98924162.386
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6101345543.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 97268.635
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```



###用例4：单broker，生产者，单线程，六分区，异步，消息payload 10000字节

#### CM：157.110

```shell
[root@lv110 KAFKA]# bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  600000 --throughput 100000 --record-size 10000 --producer-props bootstrap.servers=10.45.157.110:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
55753 records sent, 11141.7 records/sec (106.26 MB/sec), 542.1 ms avg latency, 645.0 max latency.
49782 records sent, 9956.4 records/sec (94.95 MB/sec), 665.3 ms avg latency, 784.0 max latency.
45390 records sent, 9078.0 records/sec (86.57 MB/sec), 737.3 ms avg latency, 938.0 max latency.
59220 records sent, 11844.0 records/sec (112.95 MB/sec), 570.4 ms avg latency, 837.0 max latency.
65154 records sent, 13030.8 records/sec (124.27 MB/sec), 512.4 ms avg latency, 687.0 max latency.
56700 records sent, 11340.0 records/sec (108.15 MB/sec), 575.7 ms avg latency, 895.0 max latency.
63174 records sent, 12401.6 records/sec (118.27 MB/sec), 530.8 ms avg latency, 794.0 max latency.
51438 records sent, 10287.6 records/sec (98.11 MB/sec), 645.9 ms avg latency, 1035.0 max latency.
69150 records sent, 13830.0 records/sec (131.89 MB/sec), 496.5 ms avg latency, 811.0 max latency.
68646 records sent, 13729.2 records/sec (130.93 MB/sec), 479.2 ms avg latency, 643.0 max latency.
600000 records sent, 11710.058941 records/sec (111.68 MB/sec), 564.12 ms avg latency, 1035.00 ms max latency, 549 ms 50th, 807 ms 95th, 921 ms 99th, 1020 ms 99.9th.
```

<details>
<summary>展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 10072.000
producer-metrics:batch-size-max:{client-id=producer-1}                               : 10072.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.768
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 39237556004.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.039
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 409642.999
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 21000758.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.101
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 26960.257
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.454
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 120866.909
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 23292866272.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5195645982.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 51.264
producer-metrics:network-io-rate:{client-id=producer-1}                              : 3901.110
producer-metrics:network-io-total:{client-id=producer-1}                             : 6074400849.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 118073653.956
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6053400091.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 561.486
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 1028.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 11710.745
producer-metrics:record-send-total:{client-id=producer-1}                            : 600000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 10087.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 10087.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 6.000
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.536
producer-metrics:request-latency-max:{client-id=producer-1}                          : 252.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 1950.593
producer-metrics:request-size-avg:{client-id=producer-1}                             : 60532.185
producer-metrics:request-size-max:{client-id=producer-1}                             : 60534.000
producer-metrics:request-total:{client-id=producer-1}                                : 6053400091.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 1950.631
producer-metrics:response-total:{client-id=producer-1}                               : 21000758.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 3757.653
producer-metrics:select-total:{client-id=producer-1}                                 : 23292866272.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 10.065
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 409840.788
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 21000242.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 1.307
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 118135868.231
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 6053400024.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 2.536
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 252.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.039
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 1951.582
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 33.500
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 60533.395
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : 43.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 60534.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 6053400024.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.039
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 1951.620
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 21000242.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 117952921.888
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6043200000.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 11710.973
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 600000.000
20/03/24 15:15:43 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms.
</code></pre>
</details>

#### ZFM：157.111

```shell
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  600000 --throughput 100000 --record-size 10000 --producer-props bootstrap.servers=10.45.157.111:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
65185 records sent, 13037.0 records/sec (124.33 MB/sec), 460.9 ms avg latency, 617.0 max latency.
63708 records sent, 12741.6 records/sec (121.51 MB/sec), 515.1 ms avg latency, 689.0 max latency.
65268 records sent, 13040.6 records/sec (124.36 MB/sec), 518.5 ms avg latency, 685.0 max latency.
72186 records sent, 14437.2 records/sec (137.68 MB/sec), 455.4 ms avg latency, 634.0 max latency.
72234 records sent, 14446.8 records/sec (137.78 MB/sec), 459.3 ms avg latency, 625.0 max latency.
51702 records sent, 10340.4 records/sec (98.61 MB/sec), 636.7 ms avg latency, 714.0 max latency.
56058 records sent, 11211.6 records/sec (106.92 MB/sec), 568.2 ms avg latency, 845.0 max latency.
66438 records sent, 13287.6 records/sec (126.72 MB/sec), 536.4 ms avg latency, 886.0 max latency.
61650 records sent, 12330.0 records/sec (117.59 MB/sec), 527.7 ms avg latency, 650.0 max latency.
600000 records sent, 12676.145607 records/sec (120.89 MB/sec), 518.55 ms avg latency, 886.00 ms max latency, 528 ms 50th, 671 ms 95th, 855 ms 99th, 878 ms 99.9th.
```

<details>
<summary>其他指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 10072.000
producer-metrics:batch-size-max:{client-id=producer-1}                               : 10072.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.810
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 38098753643.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.042
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 444422.864
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 21000758.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.117
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 29129.375
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.386
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 96266.318
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 18299360711.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5537232109.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 47.249
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4232.394
producer-metrics:network-io-total:{client-id=producer-1}                             : 6074400849.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 128098021.225
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6053400091.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 516.124
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 885.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 12706.211
producer-metrics:record-send-total:{client-id=producer-1}                            : 600000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 10087.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 10087.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 6.000
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.334
producer-metrics:request-latency-max:{client-id=producer-1}                          : 350.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2116.197
producer-metrics:request-size-avg:{client-id=producer-1}                             : 60532.185
producer-metrics:request-size-max:{client-id=producer-1}                             : 60534.000
producer-metrics:request-total:{client-id=producer-1}                                : 6053400091.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2116.286
producer-metrics:response-total:{client-id=producer-1}                               : 21000758.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 4011.713
producer-metrics:select-total:{client-id=producer-1}                                 : 18299360711.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 10.919
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 444684.849
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 21000242.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 1.418
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 128179393.216
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 6053400024.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 2.334
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 350.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.042
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 2117.499
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 33.500
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 60533.395
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : 43.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 60534.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 6053400024.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.042
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 2117.544
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 21000242.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 127979669.632
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6043200000.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 12706.211
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 600000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```



### 用例5：单broker，生产者，单线程，六分区，异步，消息payload 100000字节

#### CM：157.110

```shell
[root@lv110 KAFKA]# bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  180000 --throughput 100000 --record-size 100000 --producer-props bootstrap.servers=10.45.157.110:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
11869 records sent, 2373.8 records/sec (226.38 MB/sec), 266.6 ms avg latency, 337.0 max latency.
11958 records sent, 2391.6 records/sec (228.08 MB/sec), 279.4 ms avg latency, 401.0 max latency.
11646 records sent, 2329.2 records/sec (222.13 MB/sec), 289.5 ms avg latency, 379.0 max latency.
12630 records sent, 2525.5 records/sec (240.85 MB/sec), 265.6 ms avg latency, 323.0 max latency.
10434 records sent, 2081.8 records/sec (198.54 MB/sec), 320.1 ms avg latency, 574.0 max latency.
12504 records sent, 2500.3 records/sec (238.45 MB/sec), 268.9 ms avg latency, 344.0 max latency.
12552 records sent, 2505.9 records/sec (238.98 MB/sec), 265.4 ms avg latency, 335.0 max latency.
13536 records sent, 2707.2 records/sec (258.18 MB/sec), 249.0 ms avg latency, 331.0 max latency.
13464 records sent, 2683.1 records/sec (255.88 MB/sec), 249.8 ms avg latency, 360.0 max latency.
13896 records sent, 2775.3 records/sec (264.67 MB/sec), 241.7 ms avg latency, 318.0 max latency.
12576 records sent, 2514.7 records/sec (239.82 MB/sec), 265.4 ms avg latency, 371.0 max latency.
12606 records sent, 2517.7 records/sec (240.10 MB/sec), 266.7 ms avg latency, 306.0 max latency.
13716 records sent, 2743.2 records/sec (261.61 MB/sec), 244.9 ms avg latency, 311.0 max latency.
13560 records sent, 2712.0 records/sec (258.64 MB/sec), 246.5 ms avg latency, 345.0 max latency.
180000 records sent, 2529.262158 records/sec (241.21 MB/sec), 263.96 ms avg latency, 574.00 ms max latency, 259 ms 50th, 322 ms 95th, 376 ms 99th, 560 ms 99.9th.
```

<details>
<summary>更多指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 100072.000
producer-metrics:batch-size-max:{client-id=producer-1}                               : 100072.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.745
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 52979554972.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 92609.551
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 6300758.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.172
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 55881.917
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.426
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 138604.526
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 30673802862.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 12070131471.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 71.164
producer-metrics:network-io-rate:{client-id=producer-1}                              : 882.004
producer-metrics:network-io-total:{client-id=producer-1}                             : 18022320849.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 264829499.016
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 18016020091.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 248.821
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 363.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 2646.673
producer-metrics:record-send-total:{client-id=producer-1}                            : 180000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 100087.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 100087.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 6.000
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 3.900
producer-metrics:request-latency-max:{client-id=producer-1}                          : 36.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 440.990
producer-metrics:request-size-avg:{client-id=producer-1}                             : 600534.000
producer-metrics:request-size-max:{client-id=producer-1}                             : 600534.000
producer-metrics:request-total:{client-id=producer-1}                                : 18016020091.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 440.998
producer-metrics:response-total:{client-id=producer-1}                               : 6300758.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 3070.133
producer-metrics:select-total:{client-id=producer-1}                                 : 30673802862.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 92615.830
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 6300242.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 264837566.921
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 18016020024.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 3.900
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 36.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 441.003
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 600534.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 600534.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 18016020024.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 441.028
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 6300242.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 264856090.684
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 18012960000.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 2646.591
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 180000.000
20/03/24 15:33:52 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms.
</code></pre>
</details>

#### ZFM：157.111

```shell
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  180000 --throughput 100000 --record-size 100000 --producer-props bootstrap.servers=10.45.157.111:9092 acks=1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
10387 records sent, 2077.0 records/sec (198.08 MB/sec), 298.0 ms avg latency, 436.0 max latency.
11814 records sent, 2358.6 records/sec (224.93 MB/sec), 282.9 ms avg latency, 352.0 max latency.
9318 records sent, 1860.6 records/sec (177.44 MB/sec), 349.7 ms avg latency, 668.0 max latency.
12090 records sent, 2417.5 records/sec (230.55 MB/sec), 284.7 ms avg latency, 507.0 max latency.
11838 records sent, 2363.8 records/sec (225.43 MB/sec), 286.9 ms avg latency, 599.0 max latency.
12804 records sent, 2557.2 records/sec (243.88 MB/sec), 262.0 ms avg latency, 335.0 max latency.
12366 records sent, 2472.7 records/sec (235.82 MB/sec), 269.8 ms avg latency, 386.0 max latency.
12630 records sent, 2525.0 records/sec (240.80 MB/sec), 266.3 ms avg latency, 347.0 max latency.
13128 records sent, 2625.1 records/sec (250.35 MB/sec), 254.8 ms avg latency, 336.0 max latency.
13704 records sent, 2740.3 records/sec (261.33 MB/sec), 245.1 ms avg latency, 331.0 max latency.
12126 records sent, 2424.7 records/sec (231.24 MB/sec), 275.6 ms avg latency, 692.0 max latency.
12216 records sent, 2442.7 records/sec (232.96 MB/sec), 272.8 ms avg latency, 431.0 max latency.
12588 records sent, 2517.1 records/sec (240.05 MB/sec), 267.8 ms avg latency, 409.0 max latency.
12756 records sent, 2550.7 records/sec (243.25 MB/sec), 263.1 ms avg latency, 347.0 max latency.
180000 records sent, 2425.777934 records/sec (231.34 MB/sec), 274.92 ms avg latency, 692.00 ms max latency, 263 ms 50th, 363 ms 95th, 524 ms 99th, 667 ms 99.9t
```

<details>
<summary>展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 100072.000
producer-metrics:batch-size-max:{client-id=producer-1}                               : 100072.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.760
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 56589914621.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 88459.638
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 6300758.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.178
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 54098.592
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.470
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 142876.816
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 35243207817.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 13016808948.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 74.107
producer-metrics:network-io-rate:{client-id=producer-1}                              : 842.457
producer-metrics:network-io-total:{client-id=producer-1}                             : 18022320849.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 252966762.360
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 18016020091.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 260.588
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 688.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 2527.162
producer-metrics:record-send-total:{client-id=producer-1}                            : 180000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 100087.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 100087.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 6.000
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 3.990
producer-metrics:request-latency-max:{client-id=producer-1}                          : 386.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 421.227
producer-metrics:request-size-avg:{client-id=producer-1}                             : 600534.000
producer-metrics:request-size-max:{client-id=producer-1}                             : 600534.000
producer-metrics:request-total:{client-id=producer-1}                                : 18016020091.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 421.236
producer-metrics:response-total:{client-id=producer-1}                               : 6300758.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 3291.871
producer-metrics:select-total:{client-id=producer-1}                                 : 35243207817.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 88442.867
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 6300242.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 252905178.558
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 18016020024.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 3.990
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 386.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 421.134
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 600534.000
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 600534.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 18016020024.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 421.157
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 6300242.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 252898125.536
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 18012960000.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 2527.104
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 180000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```

###用例6：单broker，生产者，单线程，六分区，同步，消息payload 1000字节

#### CM：157.110

```shell
[root@lv110 KAFKA]#  bin/kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 1000 --producer-props bootstrap.servers=10.45.157.110:9092 acks=-1 buffer.memory=67108864 batch.size=8196
```

测试结果

```
453121 records sent, 90624.2 records/sec (86.43 MB/sec), 357.2 ms avg latency, 469.0 max latency.
439008 records sent, 87731.4 records/sec (83.67 MB/sec), 665.0 ms avg latency, 838.0 max latency.
426672 records sent, 85334.4 records/sec (81.38 MB/sec), 765.3 ms avg latency, 918.0 max latency.
490704 records sent, 98140.8 records/sec (93.59 MB/sec), 677.7 ms avg latency, 796.0 max latency.
529536 records sent, 105907.2 records/sec (101.00 MB/sec), 614.9 ms avg latency, 703.0 max latency.
573648 records sent, 114729.6 records/sec (109.41 MB/sec), 581.0 ms avg latency, 745.0 max latency.
541632 records sent, 108326.4 records/sec (103.31 MB/sec), 314.7 ms avg latency, 536.0 max latency.
506544 records sent, 101308.8 records/sec (96.62 MB/sec), 550.1 ms avg latency, 741.0 max latency.
464112 records sent, 92822.4 records/sec (88.52 MB/sec), 561.0 ms avg latency, 738.0 max latency.
575825 records sent, 115165.0 records/sec (109.83 MB/sec), 372.3 ms avg latency, 731.0 max latency.
483485 records sent, 96697.0 records/sec (92.22 MB/sec), 79.1 ms avg latency, 190.0 max latency.
468080 records sent, 93616.0 records/sec (89.28 MB/sec), 382.5 ms avg latency, 536.0 max latency.
6000000 records sent, 99258.867125 records/sec (94.66 MB/sec), 489.17 ms avg latency, 918.00 ms max latency, 520 ms 50th, 774 ms 95th, 855 ms 99th, 910 ms 99.9th.
```

<details>
<summary>更多指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : unknown
app-info:version:{client-id=producer-1}                                              : 1.0.1-kafka-3.1.0-SNAPSHOT
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 8016.735
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8133.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.357
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 19042441958.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 449442.767
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 26451998.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.096
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 3177.849
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.580
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 19215.984
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 33913361987.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5927126097.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 60.469
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4288.728
producer-metrics:network-io-total:{client-id=producer-1}                             : 6139398691.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 103127637.724
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6112946693.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 368.916
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 739.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 101147.817
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 1086.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 1086.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 47.199
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.236
producer-metrics:request-latency-max:{client-id=producer-1}                          : 83.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2144.353
producer-metrics:request-size-avg:{client-id=producer-1}                             : 48092.669
producer-metrics:request-size-max:{client-id=producer-1}                             : 48900.000
producer-metrics:request-total:{client-id=producer-1}                                : 6112946693.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2144.460
producer-metrics:response-total:{client-id=producer-1}                               : 26451998.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 30157.125
producer-metrics:select-total:{client-id=producer-1}                                 : 33913361987.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-22}     : 449234.005
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-22}    : 26451482.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-22}     : 103075710.033
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-22}    : 6112946626.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-22}    : 2.236
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-22}    : 83.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-22}           : 2143.341
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-22}       : 48091.146
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-22}       : 48900.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-22}          : 6112946626.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-22}          : 2143.472
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-22}         : 26451482.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 102844396.804
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6100092890.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 101148.155
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
20/03/24 16:58:14 INFO producer.KafkaProducer: [Producer clientId=producer-1] Closing the Kafka producer with timeoutMillis = 9223372036854775807 ms.
</code></pre>
</details>

#### ZFM：157.111

```shell
[root@lv111 kafka]# bin/kafka-run-class.sh org.apache.kafka.tools.ProducerPerformance --print-metrics --topic test-rep-one --num-records  6000000 --throughput 100000 --record-size 1000 --producer-props bootstrap.servers=10.45.157.111:9092 acks=-1 buffer.memory=67108864 batch.size=8196
```

```
466218 records sent, 93243.6 records/sec (88.92 MB/sec), 215.1 ms avg latency, 339.0 max latency.
485328 records sent, 97065.6 records/sec (92.57 MB/sec), 392.3 ms avg latency, 488.0 max latency.
486672 records sent, 97334.4 records/sec (92.83 MB/sec), 532.7 ms avg latency, 622.0 max latency.
508416 records sent, 101683.2 records/sec (96.97 MB/sec), 466.8 ms avg latency, 656.0 max latency.
464592 records sent, 92918.4 records/sec (88.61 MB/sec), 536.9 ms avg latency, 854.0 max latency.
443472 records sent, 88694.4 records/sec (84.59 MB/sec), 750.3 ms avg latency, 1221.0 max latency.
531927 records sent, 106385.4 records/sec (101.46 MB/sec), 615.9 ms avg latency, 761.0 max latency.
528633 records sent, 105726.6 records/sec (100.83 MB/sec), 625.6 ms avg latency, 760.0 max latency.
494736 records sent, 98947.2 records/sec (94.36 MB/sec), 663.9 ms avg latency, 831.0 max latency.
590509 records sent, 118101.8 records/sec (112.63 MB/sec), 182.0 ms avg latency, 582.0 max latency.
435911 records sent, 87182.2 records/sec (83.14 MB/sec), 398.1 ms avg latency, 645.0 max latency.
461184 records sent, 92236.8 records/sec (87.96 MB/sec), 709.4 ms avg latency, 814.0 max latency.
6000000 records sent, 98223.786527 records/sec (93.67 MB/sec), 505.40 ms avg latency, 1221.00 ms max latency, 542 ms 50th, 760 ms 95th, 977 ms 99th, 1199 ms 99.9th.

```

<details>
<summary>更多指标，展开查看</summary>
<pre><code>
Metric Name                                                                            Value
app-info:commit-id:{client-id=producer-1}                                            : c0518aa65f25317e
app-info:version:{client-id=producer-1}                                              : 1.0.1
kafka-metrics-count:count:{client-id=producer-1}                                     : 94.000
producer-metrics:batch-size-avg:{client-id=producer-1}                               : 8037.071
producer-metrics:batch-size-max:{client-id=producer-1}                               : 8133.000
producer-metrics:batch-split-rate:{client-id=producer-1}                             : 0.000
producer-metrics:batch-split-total:{client-id=producer-1}                            : 0.000
producer-metrics:buffer-available-bytes:{client-id=producer-1}                       : 67108864.000
producer-metrics:buffer-exhausted-rate:{client-id=producer-1}                        : 0.000
producer-metrics:buffer-exhausted-total:{client-id=producer-1}                       : 0.000
producer-metrics:buffer-total-bytes:{client-id=producer-1}                           : 67108864.000
producer-metrics:bufferpool-wait-ratio:{client-id=producer-1}                        : 0.495
producer-metrics:bufferpool-wait-time-total:{client-id=producer-1}                   : 18606236714.000
producer-metrics:compression-rate-avg:{client-id=producer-1}                         : 1.000
producer-metrics:connection-close-rate:{client-id=producer-1}                        : 0.000
producer-metrics:connection-close-total:{client-id=producer-1}                       : 0.000
producer-metrics:connection-count:{client-id=producer-1}                             : 2.000
producer-metrics:connection-creation-rate:{client-id=producer-1}                     : 0.000
producer-metrics:connection-creation-total:{client-id=producer-1}                    : 2.000
producer-metrics:failed-authentication-rate:{client-id=producer-1}                   : 0.000
producer-metrics:failed-authentication-total:{client-id=producer-1}                  : 0.000
producer-metrics:incoming-byte-rate:{client-id=producer-1}                           : 447420.832
producer-metrics:incoming-byte-total:{client-id=producer-1}                          : 26419418.000
producer-metrics:io-ratio:{client-id=producer-1}                                     : 0.097
producer-metrics:io-time-ns-avg:{client-id=producer-1}                               : 7965.790
producer-metrics:io-wait-ratio:{client-id=producer-1}                                : 0.537
producer-metrics:io-wait-time-ns-avg:{client-id=producer-1}                          : 43869.756
producer-metrics:io-waittime-total:{client-id=producer-1}                            : 34035696145.000
producer-metrics:iotime-total:{client-id=producer-1}                                 : 5665767926.000
producer-metrics:metadata-age:{client-id=producer-1}                                 : 61.007
producer-metrics:network-io-rate:{client-id=producer-1}                              : 4268.049
producer-metrics:network-io-total:{client-id=producer-1}                             : 6139293777.000
producer-metrics:outgoing-byte-rate:{client-id=producer-1}                           : 102922895.940
producer-metrics:outgoing-byte-total:{client-id=producer-1}                          : 6112874359.000
producer-metrics:produce-throttle-time-avg:{client-id=producer-1}                    : 0.000
producer-metrics:produce-throttle-time-max:{client-id=producer-1}                    : 0.000
producer-metrics:record-error-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-error-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-queue-time-avg:{client-id=producer-1}                        : 519.718
producer-metrics:record-queue-time-max:{client-id=producer-1}                        : 829.000
producer-metrics:record-retry-rate:{client-id=producer-1}                            : 0.000
producer-metrics:record-retry-total:{client-id=producer-1}                           : 0.000
producer-metrics:record-send-rate:{client-id=producer-1}                             : 101011.428
producer-metrics:record-send-total:{client-id=producer-1}                            : 6000000.000
producer-metrics:record-size-avg:{client-id=producer-1}                              : 1086.000
producer-metrics:record-size-max:{client-id=producer-1}                              : 1086.000
producer-metrics:records-per-request-avg:{client-id=producer-1}                      : 47.334
producer-metrics:request-latency-avg:{client-id=producer-1}                          : 2.263
producer-metrics:request-latency-max:{client-id=producer-1}                          : 65.000
producer-metrics:request-rate:{client-id=producer-1}                                 : 2134.013
producer-metrics:request-size-avg:{client-id=producer-1}                             : 48228.195
producer-metrics:request-size-max:{client-id=producer-1}                             : 48900.000
producer-metrics:request-total:{client-id=producer-1}                                : 6112874359.000
producer-metrics:requests-in-flight:{client-id=producer-1}                           : 0.000
producer-metrics:response-rate:{client-id=producer-1}                                : 2134.178
producer-metrics:response-total:{client-id=producer-1}                               : 26419418.000
producer-metrics:select-rate:{client-id=producer-1}                                  : 12233.361
producer-metrics:select-total:{client-id=producer-1}                                 : 34035696145.000
producer-metrics:successful-authentication-rate:{client-id=producer-1}               : 0.000
producer-metrics:successful-authentication-total:{client-id=producer-1}              : 0.000
producer-metrics:waiting-threads:{client-id=producer-1}                              : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:incoming-byte-rate:{client-id=producer-1, node-id=node-25}     : 447398.167
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node--1}    : 516.000
producer-node-metrics:incoming-byte-total:{client-id=producer-1, node-id=node-25}    : 26418902.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node--1}     : 0.000
producer-node-metrics:outgoing-byte-rate:{client-id=producer-1, node-id=node-25}     : 102918221.096
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node--1}    : 67.000
producer-node-metrics:outgoing-byte-total:{client-id=producer-1, node-id=node-25}    : 6112874292.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node--1}    : 0.000
producer-node-metrics:request-latency-avg:{client-id=producer-1, node-id=node-25}    : 2.263
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node--1}    : -Infinity
producer-node-metrics:request-latency-max:{client-id=producer-1, node-id=node-25}    : 65.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node--1}           : 0.000
producer-node-metrics:request-rate:{client-id=producer-1, node-id=node-25}           : 2134.013
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node--1}       : 0.000
producer-node-metrics:request-size-avg:{client-id=producer-1, node-id=node-25}       : 48227.544
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node--1}       : -Infinity
producer-node-metrics:request-size-max:{client-id=producer-1, node-id=node-25}       : 48900.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node--1}          : 67.000
producer-node-metrics:request-total:{client-id=producer-1, node-id=node-25}          : 6112874292.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node--1}          : 0.000
producer-node-metrics:response-rate:{client-id=producer-1, node-id=node-25}          : 2134.142
producer-node-metrics:response-total:{client-id=producer-1, node-id=node--1}         : 516.000
producer-node-metrics:response-total:{client-id=producer-1, node-id=node-25}         : 26418902.000
producer-topic-metrics:byte-rate:{client-id=producer-1, topic=test-rep-one}          : 102698595.622
producer-topic-metrics:byte-total:{client-id=producer-1, topic=test-rep-one}         : 6100037110.000
producer-topic-metrics:compression-rate:{client-id=producer-1, topic=test-rep-one}   : 1.000
producer-topic-metrics:record-error-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-error-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-retry-rate:{client-id=producer-1, topic=test-rep-one}  : 0.000
producer-topic-metrics:record-retry-total:{client-id=producer-1, topic=test-rep-one} : 0.000
producer-topic-metrics:record-send-rate:{client-id=producer-1, topic=test-rep-one}   : 101006.779
producer-topic-metrics:record-send-total:{client-id=producer-1, topic=test-rep-one}  : 6000000.000
</code></pre>
</details>

#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```

### 用例7：单broker，消费者，单线程，六分区

#### CM：157.110

```shell
[root@lv110 KAFKA]# bin/kafka-consumer-perf-test --broker-list 10.45.157.110:9092 --messages 6000000 --threads 1 --topic test-rep-one --print-metrics
```

测试结果

```
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2020-03-25 08:58:03:232, 2020-03-25 08:58:10:283, 571.9707, 81.1191, 6000000, 850943.1286, 3115, 3936, 145.3178, 1524390.2439
```



#### ZFM：157.111

```shell
[root@lv111 kafka]# bin/kafka-consumer-perf-test.sh --broker-list 10.45.157.111:9092 --messages 6000000 --threads 1 --topic test-rep-one --print-metrics
```

测试结果

```
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2020-03-25 09:02:23:177, 2020-03-25 09:02:30:440, 571.7060, 78.7149, 6000000, 826104.9153, 3112, 4151, 137.7273, 1445434.8350
```



#### 结果对比

```
同等测试用例下，两个机器的测试性能结果接近。
```



## 五、结论

1、在相同配置157.110和157.111两台服务器测试如上列举的用例1-用例6，所得kafka的producer吞吐性能测试结果接近。

2、在相同配置157.110和157.111两台服务器测试如上列举的用例7，所得kafka的consumer消费能力测试结果接近。（用例偏少）

