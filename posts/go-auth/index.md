# 使用Go&#43;Gin&#43;Redis实现一个简单的登录注册系统


## 简易前端 

我们先随便写一个简单的前端页面，放在工作目录下`./templates`文件夹中。

```html
&lt;html lang=&#34;en&#34;&gt;
&lt;head&gt;
    &lt;meta charset=&#34;UTF-8&#34;&gt;
    &lt;meta name=&#34;viewport&#34; content=&#34;width=device-width, initial-scale=1.0&#34;&gt;
    &lt;meta http-equiv=&#34;X-UA-Compatible&#34; content=&#34;ie=edge&#34;&gt;
    &lt;title&gt;Document&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;form action=&#34;http://47.108.140.140:8080/loginform&#34; method=&#34;post&#34;&gt;
    用户名：&lt;input type=&#34;text&#34; name=&#34;username&#34; placeholder=&#34;请输入你的用户名&#34;&gt; &lt;br&gt;
    密&amp;nbsp;&amp;nbsp;&amp;nbsp;码：&lt;input type=&#34;password&#34; name=&#34;password&#34; placeholder=&#34;请输入你的密码&#34;&gt; &lt;br&gt;
    &lt;input type=&#34;submit&#34; value=&#34;登录&#34;&gt;
&lt;/form&gt;
&lt;p&gt; ============OR============= &lt;/p&gt;
&lt;form action=&#34;http://47.108.140.140:8080/registerform&#34; method=&#34;post&#34;&gt;
    用户名：&lt;input type=&#34;text&#34; name=&#34;username&#34; placeholder=&#34;请输入你的用户名&#34;&gt; &lt;br&gt;
    密&amp;nbsp;&amp;nbsp;&amp;nbsp;码：&lt;input type=&#34;password&#34; name=&#34;password&#34; placeholder=&#34;请输入你的密码&#34;&gt; &lt;br&gt;
    &lt;input type=&#34;submit&#34; value=&#34;注册&#34;&gt;
&lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

由于不是重点，这里不详细介绍前端功能

## Gin响应请求的基本方法

```go
package main

import (
	&#34;github.com/gin-gonic/gin&#34;
	&#34;net/http&#34;
)

func main() {
	r := gin.Default()
	r.GET(&#34;/getroute&#34;, getfunction)
	r.POST(&#34;/postroute&#34;, postfunction)
	r.Run(&#34;:8080&#34;)
}
```

## 响应GET请求：返回`index.html`

```go
r.LoadHTMLGlob(&#34;templates/*&#34;) //载入templates文件夹下的所有文件
r.GET(&#34;/login&#34;, func(context *gin.Context) {
	context.HTML(http.StatusOK, &#34;index.html&#34;, gin.H {
			title&#34; :&#34;Auth&#34;,
	})
})
```

## 响应POST请求：返回登录状态

```go
r.POST(&#34;/loginform&#34;, func(context *gin.Context) {
	username := context.PostForm(&#34;username&#34;)
	password := context.PostForm(&#34;password&#34;)
	rdb, err := redis.Dial(&#34;tcp&#34;,&#34;127.0.0.1:6379&#34;)
    //连接Redis数据库
	if err != nil {
		panic(err)
	}
	exists, err := redis.Bool(rdb.Do(&#34;EXISTS&#34;, username))
	if exists != true {
		defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			&#34;message&#34; :	&#34;用户名不存在&#34;,
		})
		return
	}
	res, err := rdb.Do(&#34;Get&#34;, username)
	passget := string(res.([]byte))
	if passget != password {
		defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			&#34;message&#34; :	&#34;用户名或密码错误&#34;,
		})
		return
	}
	if err != nil {
		panic(err)
	}
    defer rdb.Close()
	context.JSON(http.StatusOK, gin.H {
		&#34;message&#34; :	&#34;登录成功&#34;,
	})
})
```

## 完整代码

```go
package main

import (
	&#34;github.com/gin-gonic/gin&#34;
	&#34;net/http&#34;
	&#34;github.com/garyburd/redigo/redis&#34;
)

func main() {
	r := gin.Default()
	r.LoadHTMLGlob(&#34;templates/*&#34;)
	r.GET(&#34;/login&#34;, func(context *gin.Context) {
		context.HTML(http.StatusOK, &#34;index.html&#34;, gin.H {
			&#34;title&#34; :&#34;Auth&#34;,
		})
	})
	r.POST(&#34;/loginform&#34;, func(context *gin.Context) {
		username := context.PostForm(&#34;username&#34;)
		password := context.PostForm(&#34;password&#34;)
		rdb, err := redis.Dial(&#34;tcp&#34;,&#34;127.0.0.1:6379&#34;)
		if err != nil {
			panic(err)
		}
		exists, err := redis.Bool(rdb.Do(&#34;EXISTS&#34;, username))
		if exists != true {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				&#34;message&#34; :	&#34;用户名不存在&#34;,
			})
			return
		}
		res, err := rdb.Do(&#34;Get&#34;, username)
		passget := string(res.([]byte))
		if passget != password {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				&#34;message&#34; :	&#34;用户名或密码错误&#34;,
			})
			return
		}
		if err != nil {
			panic(err)
		}
    	defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			&#34;message&#34; :	&#34;登录成功&#34;,
		})
	})
	r.POST(&#34;/registerform&#34;, func(context *gin.Context) {
		username := context.PostForm(&#34;username&#34;)
		password := context.PostForm(&#34;password&#34;)
		rdb, err := redis.Dial(&#34;tcp&#34;,&#34;127.0.0.1:6379&#34;)
		if err != nil {
			panic(err)
		}
		exists, err := redis.Bool(rdb.Do(&#34;EXISTS&#34;, username))
		if exists == true {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				&#34;message&#34; :	&#34;用户名已存在&#34;,
			})
			return
		}
		_, err = rdb.Do(&#34;Set&#34;, username, password)
		if err != nil {
			panic(err)
		}
    	defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			&#34;message&#34; :	&#34;注册成功&#34;,
		})
	})
	r.Run(&#34;:8080&#34;)
}
```



---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/go-auth/  

