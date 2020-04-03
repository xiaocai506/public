#!/bin/bash
echo /disk1/data/dfs/nn,/disk2/data/dfs/nn,/disk3/data/dfs/nn,/disk4/data/dfs/nn,/disk5/data/dfs/nn,/disk6/data/dfs/nn | xargs -d,| xargs -n1 >> /etc/hadoop/conf.hdfs/path.log
echo /disk1/data/dfs/dn,/disk2/data/dfs/dn,/disk3/data/dfs/dn,/disk4/data/dfs/dn,/disk5/data/dfs/dn,/disk6/data/dfs/dn | xargs -d,| xargs -n1 >> /etc/hadoop/conf.hdfs/path.log
echo /disk1/data/dfs/snn,/disk2/data/dfs/snn,/disk3/data/dfs/snn,/disk4/data/dfs/snn,/disk5/data/dfs/snn,/disk6/data/dfs/snn | xargs -d,| xargs -n1 >> /etc/hadoop/conf.hdfs/path.log
for i in `cat /etc/hadoop/conf.hdfs/path.log`
do 
  sed -i "s|$i|file://$i|g" /etc/hadoop/conf.hdfs/hdfs-site.xml
done
rm -rf /etc/hadoop/conf.hdfs/path.log
