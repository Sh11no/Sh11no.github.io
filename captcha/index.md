# 记一次模拟登陆和验证码绕过


## 目标需求

因为某种原因，我需要实现一个验证某组用户名和密码是否可以成功登录网站的模块。

这里的目标网站是icoding.run.

拟使用python requests模块伪造数据包来达成目标.

## 数据包分析

使用BurpSuite截获发送的数据包.比较关键的是以下两个数据包:

### 请求验证码

```
GET /verificationCode HTTP/1.1
Host: icoding.run
Sec-Ch-Ua: "Chromium";v="97", " Not;A Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
Sec-Ch-Ua-Platform: "Windows"
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: image
Referer: https://icoding.run/login
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close
```

返回数据Headers:

```
Server: nginx/1.18.0 (Ubuntu)
Date: Mon, 07 Feb 2022 09:23:01 GMT
Content-Type: image/jpeg
Connection: close
Set-Cookie: JSESSIONID=2ae541d8-248e-4cb7-ad45-9a5976222ed3; Path=/; HttpOnly
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Cache-Control: post-check=0, pre-check=0
Pragma: no-cache
Content-Length: 2127
```

返回数据的Content则是一张验证码图片.

### 登录

```
POST /login HTTP/1.1
Host: icoding.run
Cookie: JSESSIONID=bbcb8c2f-e0f5-4786-b00f-19135c215909
Content-Length: 61
Sec-Ch-Ua: "Chromium";v="97", " Not;A Brand";v="99"
Accept: application/json, text/javascript, */*; q=0.01
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
Sec-Ch-Ua-Platform: "Windows"
Origin: https://icoding.run
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://icoding.run/login
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close

username=*******&password=******&verification=8195
```

会返回登录是否成功以及失败原因（密码错误或验证码错误等）

### 分析

对于请求验证码的数据包，我们只需要直接模拟发送就可以得到验证码图片。值得关注的是返回Headers的这一行：

```
Set-Cookie: JSESSIONID=2ae541d8-248e-4cb7-ad45-9a5976222ed3; Path=/; HttpOnly
```

JSESSIONID是一个起用户标识作用的字段，在模拟发送登录数据包时我们需要同时发送这个字段。

因此我们的设计逻辑就比较清晰了：

1. 发送GET请求获得验证码图片和JSESSIONID
2. 识别验证码
3. 发送POST请求获得返回值

## 请求验证码和JSESSIONID

这部分是相对比较好实现的。

我们需要把收到的验证码保存到某个文件中。但考虑到可能的并发问题，这里选择使用随机文件名来防止两个进程同时对一个文件进行读写，这里选择使用一个随机的字符串作为文件名。

```python
def GenerateFilename():
	return r''.join(random.sample(string.ascii_letters + string.digits, 16))

def getCaptcha():
	url = "https://icoding.run/verificationCode"
	resp = requests.get(url)
    #事实证明根本不需要Headers，笑死
	sessionid = resp.headers['Set-Cookie']
	src = r'captchas/' + GenerateFilename() + r'.png'
	f = open(src, 'wb')
	f.write(resp.content)
	f.close()
	code = captcha.recognize_text(src)
    #对图片进行一个识别，将在后文介绍。
	os.remove(src)
    #防止垃圾文件堆积，在识别过后删除文件
	return code, sessionid
```

## 识别验证码

### 找轮子

从文章：《Python代码实现验证码识别，**很稳**》中拿到一个现成的轮子：

```python
import cv2 as cv
import pytesseract
from PIL import Image
 
 
def recognize_text(image):
    # 边缘保留滤波  去噪
    dst = cv.pyrMeanShiftFiltering(image, sp=10, sr=150)
    # 灰度图像
    gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
    # 二值化
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    # 形态学操作   腐蚀  膨胀
    erode = cv.erode(binary, None, iterations=2)
    dilate = cv.dilate(erode, None, iterations=1)
    cv.imshow('dilate', dilate)
    # 逻辑运算  让背景为白色  字体为黑  便于识别
    cv.bitwise_not(dilate, dilate)
    cv.imshow('binary-image', dilate)
    # 识别
    test_message = Image.fromarray(dilate)
    text = pytesseract.image_to_string(test_message)
    print(f'识别结果：{text}')
 
 
src = cv.imread(r'./test/044.png')
cv.imshow('input image', src)
recognize_text(src)
cv.waitKey(0)
cv.destroyAllWindows()
```

思路是先处理图片，然后直接进行一个OCR。

直接拿来进行一个跑，啥都识别不出来！把图片处理结果打出来一看，我都看不懂！

其实也不是这个轮子有啥问题，就是这个图片处理方式的特异性比较强，只适用于某种方式生成的验证码。对于图片结构不太一样的验证码这种处理方式就会当场去世了。

虽然但是，我们只需要针对icoding验证码来去除干扰（小黑线小点点啥的）就可以了。

### 安装依赖库

```
pip install pytesseract
pip install opencv-python
sudo apt-get install tesseract-ocr
pip install pillow
```

### 造轮子

上面那个轮子提供的图片处理基本不能作为参考。观察到验证码的主题部分为蓝色系，干扰部分是黑色的丝丝，考虑进行一个颜色的筛选，留住比较蓝的部分，去除其他部分：

```python
img = Image.open(src).convert("RGB")
width, height = img.size
LIM = 100
LIM2 = 0.4
for i in range(width):
    for j in range(height):
        R, G, B = pix = img.getpixel((i, j))
        sigma = R+G+B
        if sigma == 0:
            img.putpixel((i, j), (255, 255, 255))
            continue
        B /= sigma
        if B >= LIM2 and sigma >= LIM:
            img.putpixel((i, j), (0, 0, 0))
        else:
            img.putpixel((i, j), (255, 255, 255))
```

这里是直接根据RGB色号进行了筛选。设定了两个筛选条件：

1. RGB中蓝色占比大于某一阈值
2. 颜色不要太深（过滤黑色）

这样筛选完可以基本得到验证码的主体部分。但是现在的识别失败率依然非常高，问题在于在黑线挡住蓝色的场景下，可能会有数字被“一分为二”导致识别失败。

参考了一下刚刚的轮子，考虑套用pyrMeanShiftFiltering方法：Opencv均值漂移来让主体部分”侵蚀“掉面积较小的干扰断层。

最后使用pytesseract直接进行一个OCR识别，返回识别结果。

```python
import cv2 as cv
import pytesseract
from PIL import Image
 
 
def recognize_text(src):
    img = Image.open(src).convert("RGB")
    width, height = img.size
    LIM = 100
    LIM2 = 0.4
    for i in range(width):
        for j in range(height):
            R, G, B = pix = img.getpixel((i, j))
            sigma = R+G+B
            if sigma == 0:
                img.putpixel((i, j), (255, 255, 255))
                continue
            B /= sigma
            if B >= LIM2 and sigma >= LIM:
                img.putpixel((i, j), (0, 0, 0))
            else:
                img.putpixel((i, j), (255, 255, 255))
    img.save(src)
    image = cv.imread(src)
    #这里的交接应该有更好的传递方式？
    dst = cv.pyrMeanShiftFiltering(image, sp=6, sr=0)
    test_message = Image.fromarray(dst)
    text = pytesseract.image_to_string(test_message)
    return text

```

到这里我们的验证码识别成功率已经可以满足需求了。

## 模拟登录

意思就是获得验证码和JSSESIONID之后把数据包抄一遍发过去。我也懒得管headers里哪些是不需要的了发就完事了

```python
def trylogin(username, password):
	code, sessionid = getCaptcha()
	url = "https://icoding.run/login"
	#print(sessionid)
	headers = {
		'Cookie': sessionid,
		'Content-Length': '61',
		'Sec-Ch-Ua': '"Chromium";v="97", " Not;A Brand";v="99"',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Sec-Ch-Ua-Mobile': '?0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
		'Sec-Ch-Ua-Platform': '"Windows"',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9'
	}
	data = "username="+username+"&password="+password+"&verification="+str(code[:4])
	#print(data.encode())
	resp = requests.post(url, headers = headers, data = data)
	return resp.content
```

但是由于我们的验证码识别并不是100%准确，这样的登录尝试很可能返回”验证码错误“，故考虑使用多次试登录的方法。

```python
def login(username, password):
	for i in range(50):
		args = json.loads(trylogin(username, password).decode('utf-8'))
		#print(args['status'])
		#print(args['msg'][0])
		if args['status'] == 200:
			return True, 200
		elif args['msg'][0] != '验': #不是验证码错误，说明账号密码有问题
			return False, 200
	return False, 500 #尝试超时
```

至此大功告成。

## 完整代码

```python
import requests
import string
import os
import random
import json
import cv2 as cv
import pytesseract
from PIL import Image
 
def recognize_text(src):
    img = Image.open(src).convert("RGB")
    width, height = img.size
    LIM = 100
    LIM2 = 0.4
    for i in range(width):
        for j in range(height):
            R, G, B = pix = img.getpixel((i, j))
            #print(R, G, B)
            sigma = R+G+B
            if sigma == 0:
                img.putpixel((i, j), (255, 255, 255))
                continue
            B /= sigma
            if B >= LIM2 and sigma >= LIM:
                img.putpixel((i, j), (0, 0, 0))
            else:
                img.putpixel((i, j), (255, 255, 255))
    img.save(src)
    image = cv.imread(src)
    dst = cv.pyrMeanShiftFiltering(image, sp=6, sr=0)
    cv.imwrite("tmp.jpg", dst)
    test_message = Image.fromarray(dst)
    text = pytesseract.image_to_string(test_message)
    return text

def GenerateFilename():
	return r''.join(random.sample(string.ascii_letters + string.digits, 16))

def getCaptcha():
	url = "https://icoding.run/verificationCode"
	resp = requests.get(url)
	sessionid = resp.headers['Set-Cookie']
	src = r'captchas/' + GenerateFilename() + r'.png'
	f = open(src, 'wb')
	f.write(resp.content)
	f.close()
	code = recognize_text(src)
	os.remove(src)
	return code, sessionid

def trylogin(username, password):
	code, sessionid = getCaptcha()
	url = "https://icoding.run/login"
	headers = {
		'Cookie': sessionid,
		'Content-Length': '61',
		'Sec-Ch-Ua': '"Chromium";v="97", " Not;A Brand";v="99"',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Sec-Ch-Ua-Mobile': '?0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
		'Sec-Ch-Ua-Platform': '"Windows"',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9'
	}
	data = "username="+username+"&password="+password+"&verification="+str(code[:4])
	resp = requests.post(url, headers = headers, data = data)
	return resp.content

def login(username, password):
	for i in range(50):
		args = json.loads(trylogin(username, password).decode('utf-8'))
		if args['status'] == 200:
			return True, 200
		elif args['msg'][0] != '验':
			return False, 200
	return False, 500

```


