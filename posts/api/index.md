# 使用Flask&#43;nginx&#43;uwsgi在服务器上部署一个简单的API接口


## 整体架构

![](/images/flask.png)

（图源网络）

其中App是“应用程序”部分，负责实现功能。

WSGI，全称`Web Server Gateway Interface`，是Web服务器（Server）和Web应用程序（App）之间一个沟通的桥梁，是一种通信协议。

而Server则是Web服务器，负责接受来自外部的消息并通过WSGI转发给app进行处理。

## 需要的组件

### Python3

我这里是使用阿里云的Ubuntu20.04系统镜像，自带Python环境。如果你没有Python环境，请使用百度安装一个吧

### Flask

Flask是一个轻量级的Python web应用框架，在架构中协助我们进行APP部分的开发。

```
pip install flask
pip install flask_restful
```

### Nginx

Nginx是一个轻量级的Web服务器，在整体架构中负责Server部分。

```
sudo apt-get install nginx
```

### uwsgi

uWSGI是一个实现了WSGI协议的Web服务器。

相比于uwsgi，Nginx具备更优秀的静态内容处理能力，然后将动态内容转发给uWSGI服务器，这样可以达到相比于只用uwsgi而不使用Nginx更好的客户端相应。

```
pip insall uwsgi
```

### 宝塔Linux面板

非必须，一个辅助工具，可以帮助你更快地编辑和管理文件。

这是宝塔官网，可以在上面找到对应系统镜像的安装脚本：https://www.bt.cn/download/linux.html

如果你和我一样使用Ubuntu，直接执行以下命令吧：

```
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh &amp;&amp; sudo bash install.sh
```

执行完成后在服务器上执行`bt`来配置用户名和密码。

执行`/etc/init.d/bt default`查看面板入口，一般是`你的ip:8888/xxxxxx`的形式并访问，用上一步设置的用户名密码登录。

## 基于Flask的api编写

### 初始化Flask API

```python
from flask import Flask
from flask_restful import Resource, Api, reqparse
app = Flask(__name__)
api = Api(app)
```

### 创建端点

假设我们最后的API结果位于网站http://www.sh1no.icu，现在我们想要实现请求http://www.sh1no.icu/query来进行某种交互，则`/query`便称作我们的一个API端点。

为了创建端点，我们需要定义一个Python类，然后用`app.addresource`将其连接到所需的端点。

```python
class Query(Resource):
    #Methods
    pass

api.add_resource(Query, &#39;/query&#39;)
```

### 运行本地Server

这一切结束后，我们需要将它托管至本地进行测试。

```python
if __name__ == &#39;__main__&#39;:
    app.run(debug = True, host=&#34;0.0.0.0&#34;, port=3773)
```

### 编写API

这里以常用的post方法为例（其他方法大同小异）。我们在刚才创建的类中尝试创建一个post方法：

```python
class Query(Resource):
    def post(self):
        return {
            &#39;success&#39; : True
            &#39;code&#39; : 200
        }
   	pass
```

这样我们就编写好了一个POST访问就会返回成功的API。

众所周知，我们的API多半需要获取一些参数字段。这里以以下的请求格式为例：

```
{
	&#39;username&#39; : &#39;xxxxx&#39;,
	&#39;password&#39; : &#39;xxxxx&#39;
}
```

```python
class Query(Resource):
    def post(self):
        parser = reqparse.RequestParser() #初始化
        
        parser.add_argument(&#39;username&#39;, required = True) #添加需要的参数字段
        parser.add_argument(&#39;password&#39;, required = True)
        
        args = parser.parse_args() #将参数解析为Python字典
        #在解析为Python字典之后，既可以用Python字典方式获取字段的值
        username = args[&#39;username&#39;]
        password = args[&#39;password&#39;]
        
        #一些你需要实现的功能
        
        return {
            &#39;data&#39; : data #返回一些你需要返回的数据
            &#39;success&#39; : True
            &#39;code&#39; : 200
        }
   	pass
```

至此，一个支持POST方法的API就完成了。

Sample Code(Full version):

```python
from flask import Flask
from flask_restful import Resource, Api, reqparse
app = Flask(__name__)
api = Api(app)

class Query(Resource):
    def post(self):
        parser = reqparse.RequestParser() #初始化
        
        parser = add_argument(&#39;username&#39;, required = True) #添加需要的参数字段
        parser = add_argument(&#39;password&#39;, required = True)
        
        args = parser.parse_args() #将参数解析为Python字典
        #在解析为Python字典之后，既可以用Python字典方式获取字段的值
        username = args[&#39;username&#39;]
        password = args[&#39;password&#39;]
        
        #一些你需要实现的功能
        
        return {
            &#39;data&#39; : data #返回一些你需要返回的数据
            &#39;success&#39; : True
            &#39;code&#39; : 200
        }
   	pass
api.add_resource(Query, &#39;/query&#39;)
if __name__ == &#39;__main__&#39;:
    app.run(debug = True, host=&#34;0.0.0.0&#34;, port=3773)
    #这里开启了Debug模式，使用端口3773，当然你也可以不使用这个端口.
```

### 测试

将上述程序保存为API.py，并在本地试运行。

试试在本地编写一个测试脚本。

```python
import requests
import json

url = &#34;http://127.0.0.1:3773/query&#34;
headers = {
    &#39;Content-Type&#39; : &#39;application/json&#39;
}
data = {
    &#39;username&#39; : &#39;shino&#39;,
    &#39;password&#39; : &#39;daisuke&#39;
}
sessions = requests.session()
response = sessions.post(url, data = json.dumps(data), headers = headers, verify = False)
for what in response:
    print(what.decode())
```

运行返回：

```
{
	&#39;success&#39; : True,
	&#39;code&#39; : 200
}
```

说明API已经可以运行了。

## 配置并启动uWSGI

在项目路径下创建一个配置文件`uwsgi.ini`

这里项目路径以`/home/flask`为例。

填入以下内容：

```
[uwsgi]
# uwsgi 启动时所使用的地址与端口,也可以使用.sock文件的方式
socket = 127.0.0.1:3773
# 指向网站目录
chdir = /home/flask
# python 启动程序文件
wsgi-file = API.py
# python 程序内用以启动的 application 变量名
callable = app
# 处理器数
processes = 1
# 线程数
threads = 1
#项目flask日志文件
logto = /home/moco/www/myflask/log.log
```

以`uwsgi.ini`为配置文件启动uwsgi：

```
uwsgi --ini /home/flask/uwsgi.ini
```

## 配置并启动Nginx

配置Nginx配置文件中的`sites-enabled/default`

```
server {
    listen 1664;   #希望接收信息的端口
    server_name sh1no.icu; #好像可以不填？
    charset utf-8;
    client_max_body_size 75M;
    location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:3773; #与uwsgi启动的端口一致
    }
}
```

运行nginx：

```
service nginx start
```

你可能会用到的命令：

重新加载配置文件

```
nginx -s reload
```

（该命令需要nginx正在运行，否则会报错找不到pid）

重启nginx服务

```
service nginx restart
```

停止nginx服务

```
nginx -s stop
```

## 本地测试

还是用刚刚的测试脚本：

```python
import requests
import json

url = &#34;http://127.0.0.1:1664/query&#34; #这里改成nginx监听的端口
headers = {
    &#39;Content-Type&#39; : &#39;application/json&#39;
}
data = {
    &#39;username&#39; : &#39;shino&#39;,
    &#39;password&#39; : &#39;daisuke&#39;
}
sessions = requests.session()
response = sessions.post(url, data = json.dumps(data), headers = headers, verify = False)
for what in response:
    print(what.decode())
```

在服务器端运行，如果成功则说明nginx、uwsgi、flask三者连接完好。

## 开放防火墙设置

若将上述脚本中`127.0.0.1:1664`改成服务器的公网ip或域名无法得到回复，说明我们连接可能被防火墙阻止。

首先检查服务器提供商安全组策略是否放开端口

然后检查系统自带的防火墙。以`Ubuntu20.04`为例，`Ubuntu20.04`默认安装了`ufw`防火墙

输入：

```
sudo ufw status verbose
```

可以查看ufw的活动状态和允许的访问端口。

设置允许端口：

```
sudo ufw allow 1664
```

运行测试脚本，访问成功，大功告成！


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/api/  

