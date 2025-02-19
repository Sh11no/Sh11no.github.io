# D3CTF2022wp-BadW3ter &amp; D3bug


## BadW3ter

当时打题目名字的时候也没有多想，后来发现Water拼错了，笑死。

文件名后面的md5码可以解出来Sh1n0，是我为了混淆题目文件名随便弄的和题目没有关系（一般会去解文件名吗，还是个md5）

![1](/images/D3/1.png)

发现文件头被篡改（我超，初音未来）

![2](/images/D3/2.png)

这里只改了RIFF区块前后和FORMAT区块开头的标识符，可以相对容易地恢复成正常的文件格式，并且得到字符串`CUY1nw31lai`

根据题目提示`「Dive into」the w3ter, deeper and deeper.`使用DeepSound解密，密码为`CUY1nw31lai`得到一个flag.png，直接扫发现被骗了。

![3](/images/D3/3.png)

查看文件头，发现并不是一个PNG文件。结合开头的`II*`标识和大量的`Adobe Photoshop`注释信息可以推测出是TIF存储格式，改后缀名后用`Adobe Photoshop`打开。

事实上，当文件后缀不正确的时候Photoshop是无法打开此图片的（如下图）

![4](/images/D3/4.png)

所以也可以把所有的图片文件后缀都试一遍（？

![5](/images/D3/5.png)

发现图片包含一张透明底的二维码图片和一个白底。通过大眼观察（或是Stegsolve之类的工具）是可以发现前景的二维码图片并不是纯黑的，并且颜色分布有一点微妙。在这里刻意的分层存储和非纯色的暗示意味已经非常明显了。

使用油漆桶工具将背景改为黑色。可以发现二维码内容发生了变化：

![6](/images/D3/6.png)

用魔棒之类的工具处理一下，扫描得到flag

`D3CTF{M1r@9e_T@nK_1s_Om0sh1roiii1111!!!!!Isn&#39;t_1t?}`

参考：https://zhuanlan.zhihu.com/p/32532733

## d3bug

这个题是拿出来当签到题的。首先通过简单分析一下题目可以得到一些限制条件，用SAT、z3solver等工具可以直接出解。

如果你不愿意使用这些工具的话：

观察到在`lfsr_MyCode`部分得到的每一位`output`相当于是前面所有位的异或和。每次移位时最高位会消失，直接把这两次得到的output随意简单异或一下就可以得到这一次消失的高位。

剩下的低位通过`lfsr_CopiedfromInternet`的结果可以得到一个模二加方程组（就是传统的lfsr做法），解一下就可以了

```python
from Crypto.Util.number import *
my   = [0,0,1,0,0,1,1,0,0,0,1,0,0,0,1,1,0,0,0,1,1,0,1,0,1,0,1,0,1,0,0,1,0,0,1]
std  = [0,1,1,1,1,1,0,1,1,1,1,0,1,0,1,1,1,0,0,0,0,1,0,0,1,0,1,1,1,0,0,1,1,0,1]
mask = [1,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,0]
highbits = []

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

for i in range(1, 34):
	my[i] ^= my[i-1]

for i in range(1, 34):
	highbits.append(my[i]^my[i-1])

basepos = 0

bb = []
for i in range(31):
	res = std[i]
	aa = []
	for j in range(33-basepos):
		if mask[j] == 1:
			res ^= highbits[j&#43;basepos]
	k = 33-basepos
	for j in range(31):
		aa.append(mask[k])
		k &#43;= 1
	cnt = 0
	while k &lt; 64:
		if mask[k] == 1:
			res ^= std[cnt]
		cnt &#43;= 1
		k &#43;= 1
	aa.append(res)
	bb.append(aa)
	basepos &#43;= 1

lowbits = calculate_parameter(bb, 2, 31)
flag = 0
for i in range(33):
	flag = (flag &lt;&lt; 1) ^ highbits[i]
for i in range(31):
	flag = (flag &lt;&lt; 1) ^ lowbits[i]
print(long_to_bytes(flag))
```

得到flag：

`D3CTF{LF5Rsuk!}`


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/d3ctf2022/  

