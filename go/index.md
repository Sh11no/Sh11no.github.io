# Go语言乱学速成学习笔记


**本文基于C++、python语言基础学习.**

## 基本

示例

```  { 
package main
import "fmt"
func main() {
	fmt.Println("Hello, World!")
}
```

1、当标识符（包括常量、变量、类型、函数名、结构字段等等）以一个大写字母开头，如：Group1，那么使用这种形式的标识符的对象就可以被外部包的代码所使用（客户端程序需要先导入这个包），这被称为导出（像面向对象语言中的 public）；标识符如果以小写字母开头，则对包外是不可见的，但是他们在整个包的内部是可见并且可用的（像面向对象语言中的 protected ）

2、大括号不准换行，一行代表一个语句结束，没有分号。

3、标识符、注释规则与cpp相同。

4、变量类型：数字、字符串、布尔。

## 语法相关

### 变量相关

#### 变量声明

```go
//var v_name type
//Example:
var a string = "ABCD"
var b, c int = 1, 2
//var v_name
//Example:
var d int // 初始值为0
var e string //初始值为""
//var v_name = value
var f = true
var g = 0
//自动判断变量类型
// v_name = value
intVal := 1
//相当于:
var intVal int
intVal = 1
//这种结构只能在函数体中出现。
/*var(
	v_name1 type1
	v_name2 type2
)*/
//Example:
var (
	a int
    b bool
)
```

**函数内变量不允许声明但不使用**

#### 变量赋值

```go
a = 1
a, b = 1, 2
a, b = b, a
_, b = b, a
```

空白标识符`_`是一个只写变量，用于抛弃值。

#### 常量

##### const

使用`const`代替`var`，其余和变量声明一样。可以调用函数：

```go
const (
	a = "abc"
    b = len(a)
    c = unsafe.Sizeof(a)
)
```

函数必须是内置函数，否则会编译错误。

##### iota

不会用，不用！但是可以先记在这里。

相当于表示`const`声明的行索引。

```go
const (
	a = iota //0
	b = iota //1
	c = iota //2
)
```

可以简写成这样：

```go
const (
	a = iota //0
	b //1
	c //2
)
```

一个猜测：啥都没写的常量相当于把上一行复制一遍。

```go
const (
	a = iota   //0
	b          //1
	c          //2
	d = "ha"   //独立值，iota += 1
	e          //"ha"   iota += 1
	f = 100    //iota +=1
	g          //100  iota +=1
	h = iota   //7,恢复计数
	i          //8
)
```

```go
const (
	i = 1<<iota //1 << 0
	j = 3<<iota //3 << 1
	k			//3 << 2
	l			//3 << 3
)
```

### 运算符

全都和cpp一样。

### 语法相关

#### 条件语句

```go
if a > 20 {
	....
} else {
	....
}
```

#### 循环

##### 基本

```go
for i := 0; i <= 10; i++ {
    //普通
}
for sum <= 10 {
    //类似while
}
for {
    //无限循环
}
strings := []string{"shino", "suki"}
for i, s := range strings {
    fmt.Println(i, s) // 迭代访问数组、字符串、切片元素
}
```

##### break&continue

```go
for i := 1; i <= 3; i++ {
	fmt.Printf("i: %d\n", i)
		for i2 := 11; i2 <= 13; i2++ {
			fmt.Printf("i2: %d\n", i2)
			break
		}
}
//跳出一层循环
re:
for i := 1; i <= 3; i++ {
	fmt.Printf("i: %d\n", i)
	for i2 := 11; i2 <= 13; i2++ {
		fmt.Printf("i2: %d\n", i2)
		break re
	}
}
//跳出至标记处
```

continue同理。

#### 函数

```go
func funtion_name( [parameter list] ) [return types] {
	.....
}
```

```go
func max(a, b int) int {
	if a > b {
		return a
	} else {
		return b
	}
}
func swap1(a, b int) (int, int) {
    return b, a
} //返回多个值
func swap(x *int, y *int) {
    var tmp int
    tmp = *x
    *x = *y
    *y = tmp
}//引用传递
func main() {
    getSquareRoot := func(x float64) float64 {
        return math.Sqrt(x)
    }
    fmt.Println(getSquareRoot(9))
} //一些炫酷
```

#### 变量作用域

与C++相同。但是局部变量的默认值也是0

#### 数组

```go
var v_name [SIZE] var_type
```

```go
var a = [5]int{1, 2, 3, 4, 5}
b := [5]int{1, 3, 4, 5, 3}
c := [...]int{1, 2, 3, 4, 5} //数组长度不确定可用...代替
d := [5]int{1:2, 3:4} //仅初始化下标为1, 3的元素
e := [5][5]int{} //二维数组
```

```go
package main

import "fmt"

func main() {
    // 创建空的二维数组
    animals := [][]string{}

    // 创建三一维数组，各数组长度不同
    row1 := []string{"fish", "shark", "eel"}
    row2 := []string{"bird"}
    row3 := []string{"lizard", "salamander"}

    // 使用 append() 函数将一维数组添加到二维数组中
    animals = append(animals, row1)
    animals = append(animals, row2)
    animals = append(animals, row3)

    // 循环输出
    for i := range animals {
        fmt.Printf("Row: %v\n", i)
        fmt.Println(animals[i])
    }
}
//一些炫酷实例
```

#### 结构体

```go
type Books struct {
   title string
   author string
   subject string
   book_id int
}
func main() {
    var Book1 Books
    Book1.book_id = 3
    fmt.Println(Book1.book_id)
}
```


