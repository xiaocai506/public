# 工作日志

## 2020-3-21

### mysql的配置

参考链接https://blog.csdn.net/kong2030/article/details/85602941

https://blog.csdn.net/liu_dong_mei_mei/article/details/104010567

密码：czw2011

版本：5.7.29

### mysql_front连接报错，sql执行错误#3167的解决方案

https://blog.csdn.net/u011065164/article/details/53034298

### MySQL-Front访问数据库报错：SQL执行错误 #1055

https://blog.csdn.net/weixin_41360604/article/details/102651830

### 导入sql文件

https://jingyan.baidu.com/article/cb5d6105c4dfbe005c2fe09e.html

## 2020-3-23

### tomcat配置

https://www.cnblogs.com/killer-xc/p/7778823.html

Tomcat控制台中文乱码问题解决

https://blog.csdn.net/zymndsc_2012/article/details/85647621

 node Could not install Visual Studio Build Tools ，新版本有问题，安装4.0.0

```
npm install --global --production windows-build-tools@4.0.0
```

> 鉴于国内的环境，node-sass实在是太难安装了，可以直接通过淘宝的npm镜像来安装。
>
> 1.安装cnpm（https://npm.taobao.org/）
>
> npm install -g cnpm --registry=https://registry.npm.taobao.org
>
> 2.在项目文件夹下安装node-sass
>
> cnpm install --save-dev node-sass
>
> 说明：--save-dev自动将node-sass加入到项目文件夹下的package.json中 ---------------------
>
> 本文来自 SeekerTime 的CSDN 博客 ，全文地址请点击：https://blog.csdn.net/seekertime/article/details/68944482?utm_source=copy 2020-4-5



## 2020-4-5

### 解决maven打包编译出现File encoding has not been set问题

```
maven打包编译时后台一直输出警告信息

[WARNING] File encoding has not been set, using platform encoding GBK, i.e. build is platform dependent!
找了半天，原来只要在pom.xml文件中增加一个配置项即可
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

```

### win7 下安装kibana

https://blog.csdn.net/Soinice/article/details/87861121

### asciidoc文档转pdf

1、通过vscode的asciidoc插件先转成html（直接转pdf的不成功？）

2、借助wkhtmltopdf转成pdf文件



## 2020-4-18

easydarwin 开源流媒体服务器

> - 基于Golang开发维护；
> - 支持Windows、Linux、macOS平台；
> - 支持RTSP推流分发（推模式转发）；
> - 支持RTSP拉流分发（拉模式转发）；
> - 服务端录像 参考:https://blog.csdn.net/jyt0551/article/details/84189498
> - 服务端录像检索与回放 参考:https://blog.csdn.net/jyt0551/article/details/84189498
> - 关键帧缓存；
> - 秒开画面；
> - Web后台管理；
> - 分布式负载均衡；

ffmpeg的推流

154.73有多个ffmpeg版本，使用/opt/ffmpeg下版本

推视频文件到rtsp服务器（）

```
 /opt/ffmpeg/bin/ffmpeg -re -stream_loop -1  -i *.264 -vcodec copy  -an -f rtsp -rtsp_transport tcp rtsp://10.45.154.73:554/test.sdp
```

参考

 https://blog.csdn.net/cai6811376/article/details/74783269 

循环文件推送

```shell
#!/bin/bash
i=1
 
while (($i < 100))
do
        echo $i
        /opt/ffmpeg/bin/ffmpeg -re -i *.264 -vcodec copy  -acodec copy -f rtsp -rtsp_transport tcp rtsp://10.45.154.73:554/test.sdp
        i=$(($i+1))

done
```



推rtsp流到rtsp服务器 -an 不要音频

```
/opt/ffmpeg/bin/ffmpeg -i rtsp://admin:Znv123456@10.45.148.111:554 -vcodec copy  -an  -f rtsp -rtsp_transport tcp rtsp://10.45.154.73:554/test.sdp
```

