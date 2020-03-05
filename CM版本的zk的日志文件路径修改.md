# zk的日志路径的修改

## 开源版本的zk日志路径修改方法

参考链接

http://anlibraly.github.io/zookeeper-日志(.out&log4j)设置及清理/

## CM版本的修改方法

### 溯源zk服务的启停调用流程

```shell
root@lv123 init.d]# systemctl status zookeeper-server.service 
â— zookeeper-server.service - LSB: ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.
   Loaded: loaded (/etc/rc.d/init.d/zookeeper-server; bad; vendor preset: disabled)
   Active: active (running) since Tue 2020-03-03 10:12:55 CST; 4min 48s ago
     Docs: man:systemd-sysv-generator(8)
  Process: 189357 ExecStop=/etc/rc.d/init.d/zookeeper-server stop (code=exited, status=0/SUCCESS)
  Process: 163741 ExecStart=/etc/rc.d/init.d/zookeeper-server start (code=exited, status=0/SUCCESS)
 Main PID: 190423 (java)
   CGroup: /system.slice/zookeeper-server.service
           â€£ 190423 java -Dzookeeper.datadir.autocreate=false -Dzookeeper.log.dir=/var/log/zookeeper -Dzookeeper.root.logger=INFO,ROLLINGFIL...

Mar 03 10:12:55 lv123.dct-znv.com systemd[1]: Starting LSB: ZooKeeper is a centralized service for maintaining configuration informat...ces....
Mar 03 10:12:55 lv123.dct-znv.com su[163785]: (to zookeeper) root on none
Mar 03 10:12:55 lv123.dct-znv.com zookeeper-server[163741]: JMX enabled by default
Mar 03 10:12:55 lv123.dct-znv.com zookeeper-server[163741]: Using config: /etc/zookeeper/conf/zoo.cfg
Mar 03 10:12:55 lv123.dct-znv.com zookeeper-server[163741]: Starting zookeeper ... already running as process 190423.
Mar 03 10:12:55 lv123.dct-znv.com systemd[1]: Started LSB: ZooKeeper is a centralized service for maintaining configuration informati...vices..
Hint: Some lines were ellipsized, use -l to show in full.
```

zk服务的启停脚本为A=<font color=red>/etc/rc.d/init.d/zookeeper-server</font>

```shell
vim /etc/rc.d/init.d/zookeeper-server

```

```shell
#显示部分内容
...
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON_SCRIPT="/usr/bin/zookeeper-server"
...
tart() {
    su -s /bin/bash zookeeper -c "${DAEMON_SCRIPT} start"
}
stop() {
        if hadoop_check_pidfile $PID_FILE ;  then
        su -s /bin/bash zookeeper -c "${DAEMON_SCRIPT} stop"
        fi
}
```

A调用的脚本B=<font color=red>/usr/bin/zookeeper-server</font>

```
vim /usr/bin/zookeeper-server
```

```shell
#!/bin/bash

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

export ZOOPIDFILE=${ZOOPIDFILE:-/var/run/zookeeper/zookeeper-server.pid}
export ZOOKEEPER_HOME=${ZOOKEEPER_CONF:-/usr/lib/zookeeper}
export ZOOKEEPER_CONF=${ZOOKEEPER_CONF:-/etc/zookeeper/conf}
export ZOOCFGDIR=${ZOOCFGDIR:-$ZOOKEEPER_CONF}
export CLASSPATH=$CLASSPATH:$ZOOKEEPER_CONF:$ZOOKEEPER_HOME/*:$ZOOKEEPER_HOME/lib/*
export ZOO_LOG_DIR=${ZOO_LOG_DIR:-/var/log/zookeeper}
export ZOO_LOG4J_PROP=${ZOO_LOG4J_PROP:-INFO,ROLLINGFILE}
export JVMFLAGS=${JVMFLAGS:--Dzookeeper.log.threshold=INFO}
export ZOO_DATADIR_AUTOCREATE_DISABLE=${ZOO_DATADIR_AUTOCREATE_DISABLE:-true}
env CLASSPATH=$CLASSPATH /usr/lib/zookeeper/bin/zkServer.sh "$@"
```

B调用脚本C=<font color=red>usr/lib/zookeeper/bin/zkServer.sh</font>

在B脚本定义了ZOO_LOG_DIR ，ZOO_LOG4J_PRO，需要在此处修改