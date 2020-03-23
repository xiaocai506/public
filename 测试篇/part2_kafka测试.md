# Kafka性能测试

## 机器

## 服务配置

## 测试方案

kafka 0.8.x版本

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

Kafka 1.0.0版本

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

