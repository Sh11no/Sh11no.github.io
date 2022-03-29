# 使用Go+Gin+Redis实现一个简单的登录注册系统


## 简易前端 

我们先随便写一个简单的前端页面，放在工作目录下`./templates`文件夹中。

```html
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
<form action="http://47.108.140.140:8080/loginform" method="post">
    用户名：<input type="text" name="username" placeholder="请输入你的用户名"> <br>
    密&nbsp;&nbsp;&nbsp;码：<input type="password" name="password" placeholder="请输入你的密码"> <br>
    <input type="submit" value="登录">
</form>
<p> ============OR============= </p>
<form action="http://47.108.140.140:8080/registerform" method="post">
    用户名：<input type="text" name="username" placeholder="请输入你的用户名"> <br>
    密&nbsp;&nbsp;&nbsp;码：<input type="password" name="password" placeholder="请输入你的密码"> <br>
    <input type="submit" value="注册">
</form>
</body>
</html>
```

由于不是重点，这里不详细介绍前端功能

## Gin响应请求的基本方法

```go
package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	r := gin.Default()
	r.GET("/getroute", getfunction)
	r.POST("/postroute", postfunction)
	r.Run(":8080")
}
```

## 响应GET请求：返回`index.html`

```go
r.LoadHTMLGlob("templates/*") //载入templates文件夹下的所有文件
r.GET("/login", func(context *gin.Context) {
	context.HTML(http.StatusOK, "index.html", gin.H {
			title" :"Auth",
	})
})
```

## 响应POST请求：返回登录状态

```go
r.POST("/loginform", func(context *gin.Context) {
	username := context.PostForm("username")
	password := context.PostForm("password")
	rdb, err := redis.Dial("tcp","127.0.0.1:6379")
    //连接Redis数据库
	if err != nil {
		panic(err)
	}
	exists, err := redis.Bool(rdb.Do("EXISTS", username))
	if exists != true {
		defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			"message" :	"用户名不存在",
		})
		return
	}
	res, err := rdb.Do("Get", username)
	passget := string(res.([]byte))
	if passget != password {
		defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			"message" :	"用户名或密码错误",
		})
		return
	}
	if err != nil {
		panic(err)
	}
    defer rdb.Close()
	context.JSON(http.StatusOK, gin.H {
		"message" :	"登录成功",
	})
})
```

## 完整代码

```go
package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"github.com/garyburd/redigo/redis"
)

func main() {
	r := gin.Default()
	r.LoadHTMLGlob("templates/*")
	r.GET("/login", func(context *gin.Context) {
		context.HTML(http.StatusOK, "index.html", gin.H {
			"title" :"Auth",
		})
	})
	r.POST("/loginform", func(context *gin.Context) {
		username := context.PostForm("username")
		password := context.PostForm("password")
		rdb, err := redis.Dial("tcp","127.0.0.1:6379")
		if err != nil {
			panic(err)
		}
		exists, err := redis.Bool(rdb.Do("EXISTS", username))
		if exists != true {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				"message" :	"用户名不存在",
			})
			return
		}
		res, err := rdb.Do("Get", username)
		passget := string(res.([]byte))
		if passget != password {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				"message" :	"用户名或密码错误",
			})
			return
		}
		if err != nil {
			panic(err)
		}
    	defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			"message" :	"登录成功",
		})
	})
	r.POST("/registerform", func(context *gin.Context) {
		username := context.PostForm("username")
		password := context.PostForm("password")
		rdb, err := redis.Dial("tcp","127.0.0.1:6379")
		if err != nil {
			panic(err)
		}
		exists, err := redis.Bool(rdb.Do("EXISTS", username))
		if exists == true {
			defer rdb.Close()
			context.JSON(http.StatusOK, gin.H {
				"message" :	"用户名已存在",
			})
			return
		}
		_, err = rdb.Do("Set", username, password)
		if err != nil {
			panic(err)
		}
    	defer rdb.Close()
		context.JSON(http.StatusOK, gin.H {
			"message" :	"注册成功",
		})
	})
	r.Run(":8080")
}
```


