# 使用Nonebot2和Gocq搭建QQ机器人并部署到服务器


## 配置机器人

### QQ机器人的基本架构

这里引用一个看到过的例子：

在一个餐馆中，你点了一盘菜。此时会发生什么事情呢？

&gt; 1、服务员接受你点的菜
&gt;
&gt; 2、服务员把你点的菜告诉大厨
&gt;
&gt; 3、大厨进行一个烹饪
&gt;
&gt; 4、服务员把菜端到你桌上

在一个QQ机器人中，`go-cqhttp`就类似于一个服务员，负责接收消息、把消息传达给`nonebot2`、发送消息。而`nonebot2` 就相当于一个大厨，负责“思考”对消息该做出什么反应。

那么`go-cqhttp`如何将消息传达给`nonebot2`呢？

这里我们使用的是反向`websocket`连接：`go-cqhttp`会主动寻找`nonebot2`的程序，并将消息通过`websocket`推送给`nonebot2`。当然，如果你只是想要做出一个QQ机器人，你可以不需要深入了解该通信方式。

### 准备

我们需要：一个云服务器，nonebot2，go-cqhttp

由于nonebot2是基于python3.7&#43;的，所以我们还需要配置一个python。

**我推荐在服务器上执行命令前先使用`sudo -i`切换到管理员账户来避免一些麻烦**

#### 安装系统镜像&amp;python

首先你需要一个云服务器，并安装系统镜像。我这里选用的是`Ubuntu20.07`系统镜像，因为`Ubuntu20.07`自带一个Python3.8.10，可以省去python的配置步骤。

这一步按理来说是可以一键完成的，起码腾讯云和阿里云都有一键安装的入口。

#### 安装nonebot2

执行以下命令：

```
pip3 install nb-cli
pip3 install nonebot-adapter-cqhttp
```

如果找不到库的话，可以试试换源：

```
pip3 install nb-cli -i https://pypi.org/simple
pip3 install nonebot-adapter-cqhttp -i https://pypi.org/simple
```

#### 安装go-cqhttp

##### 下载go-cqhttp

在go-cqhttp的&lt;a href = &#34;https://github.com/Mrs4s/go-cqhttp/releases&#34;&gt;Release页面&lt;/a&gt;找到`go-cqhttp_linux_386.tar.gz`并下载。

或者直接点击&lt;a href = &#34;https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-beta7-fix2/go-cqhttp_linux_386.tar.gz&#34;&gt;这里&lt;/a&gt;下载。

这里下载的是适用于Linux的32位`go-cqhttp`，如果你是64位，请找到并下载`go-cqhttp_linux_amd64.tar.gz`

##### 将go-cqhttp上传至服务器

这里使用宝塔Linux面板辅助上传。宝塔yyds。

这是宝塔官网，可以在上面找到对应系统镜像的安装脚本：https://www.bt.cn/download/linux.html

如果你和我一样使用Ubuntu，直接执行以下命令吧：

```
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh &amp;&amp; sudo bash install.sh
```

执行完成后在服务器上执行`bt`来配置用户名和密码。

执行`/etc/init.d/bt default`查看面板入口，一般是`你的ip:8888/xxxxxx`的形式并访问，用你刚刚的用户名密码登录。

配置好宝塔之后，点击左边菜单栏中“文件“即可进行文件管理、编辑和上传。

我们在根目录新建一个`/bot`文件夹，上传go-cqhttp并解压。

如果你的宝塔并没有帮你解压成功，你可以在服务器上执行以下命令：

```
cd go-cq所在文件目录（例如cd /bot）
tar -xzvf 文件名
```

或者你也可以解压完之后再上传，反正也没有几个文件。

至此，我们需要的东西就准备好了。

### 配置

#### 配置go-cqhttp

先跑一下。

```text
cd go-cq所在文件目录
./go-cqhttp
```

出现：

```text
未找到配置文件，正在为您生成配置文件中！
请选择你需要的通信方式:
&gt; 1: HTTP通信
&gt; 2: 正向 Websocket 通信
&gt; 3: 反向 Websocket 通信
&gt; 4: pprof 性能分析服务器
请输入你需要的编号，可输入多个，同一编号也可输入多个(如: 233)
您的选择是:
```

输入3然后按回车，此时我们就会发现go-cq的文件夹里生成了一个`config.yml`，编辑并修改以下几处：

我这里是直接用宝塔进行的编辑，我也推荐各位直接使用宝塔。

```text
account: # 账号相关
  uin: 1233456 # QQ账号
```

把`uin`改为`bot`的QQ账号。不建议填写password，在不填写password时第一次将会使用扫码登录，可以避免密码登录造成的一些问题（比如滑块验证）。

```text
servers:
  # 添加方式，同一连接方式可添加多个，具体配置说明请查看文档
  #- http: # http 通信
  #- ws:   # 正向 Websocket
  #- ws-reverse: # 反向 Websocket
  #- pprof: #性能分析服务器
  # 反向WS设置
  - ws-reverse:
      # 反向WS Universal 地址
      # 注意 设置了此项地址后下面两项将会被忽略
      universal: ws://127.0.0.1:xxxx/cqhttp/ws    #修改的位置！！！
      # 反向WS API 地址
      api: ws://your_websocket_api.server
      # 反向WS Event 地址
      event: ws://your_websocket_event.server
      # 重连间隔 单位毫秒
      reconnect-interval: 3000
      middlewares:
        &lt;&lt;: *default # 引用默认中间件
```

此处把xxxx替换为端口号其他不变。不建议使用会冲突的端口号，建议从`5000-65535`取值。随意填一个数就行。

此时你可以试着运行一下go-cq

```text
cd go-cq所在文件目录
./go-cqhttp
```

如果你看到这个：

```text
[INFO]: アトリは、高性能ですから!
```

说明你成功啦！

#### 配置nonebot2

你需要新建一个文件夹给`nonebot2`。不推荐使用中文文件夹名字。这里同样使用宝塔完成操作。

新建一个`bot.py`，写入以下代码：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
#初始化nb
nonebot.init()
app = nonebot.get_asgi()
#连接驱动
driver = nonebot.get_driver()
driver.register_adapter(&#34;cqhttp&#34;, CQHTTPBot)
#加载插件(除此处其他配置不建议更改)
nonebot.load_builtin_plugins()
nonebot.load_plugins(&#39;src/plugins&#39;)
#启动bot
if __name__ == &#34;__main__&#34;:
    nonebot.logger.warning(&#34;Always use `nb run` to start the bot instead of manually running!&#34;)
    nonebot.run(app=&#34;__mp_main__:app&#34;)
```

在相同目录下创建`.env`文件，写入以下内容：

```
HOST=127.0.0.1
PORT=xxxx
DEBUG=False
SUPERUSERS=[&#34;管理员账号1&#34;,&#34;管理员账号2&#34;]
COMMAND_START=[&#34;/&#34;,&#34;!!&#34;]
```

其中`PORT`修改为刚刚你在`go-cq`配置过程中输入的端口号。

`COMMAND_START`字段是命令的起始符号，以该符号开头的将会被识别为”命令“被处理。我一般喜欢使用&#34;&#34;，即所有文字都被nonebot接收并处理。

然后我们在该目录下新建一个`src`文件夹，在`src`内再新建一个`plugins`文件夹。这里就是你存放你写的`nonebot2`插件的地方啦。

### 运行机器人

没意外的话到这里我们的机器人就已经准备好了，直接开始运行吧！

在服务器上，以腾讯云为例，每次按”登录“只会打开一个界面。但我们需要运行两个程序。咋办呢？

首先执行：

```
sudo -i
cd bot.py所在文件目录
screen
python bot.py
```

重新打开，执行：

```
sudo -i
cd go-cqhhtp所在文件目录
screen
./go-cqhttp
```

重新打开，执行：

```
sudo -i
screen -ls
```

这个时候你应该看到有两个进程正在运行。

用QQ给你的机器人发送：`/echo Hello_World!`

收到机器人的回复了！至此我们的机器人就算配置完毕了。

## 编写插件-实现你想要的功能

先鸽了。


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/bot/  

