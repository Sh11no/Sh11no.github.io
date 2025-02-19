# Hitcon2023 Reverse Wps | AK With StrawHat


## 碎碎念

应该是在 Straw Hat 队认真打的第一场国际赛事吧，可惜半天左右就把逆向全打完了（驾驶员技能发动 我一个人就够了.jpg），有些失望（但是很爽）。

写于 2023-09-09 23:25 离比赛结束还有 1day 左右，但是目前放出的 Reverse 已经全部 AK 了，没事干了写个 Writeups 先。感觉目前放出的 Reverse 难度总体偏易，大概 CrazyArcade &lt; Full Chain - The Blade &lt; LessEQualmore 吧，这里按打题顺序简单写一下复盘。

## LessEQualmore 

虚拟机的逻辑非常简单，每个指令为 3 个字长`a1 a2 a3`，假设存在`mem[]`里

逻辑伪代码大概如下：

```python
if a1 &lt; 0:
	data = input()
else:
	data = mem[a1]

if a2 &lt; 0:
    output(data)
else:
    mem[a2] = data

if mem[a2] &lt;= 0:
    jmp a3
```

然后就是逆向字节码了，这个字节码非常复杂，需要考虑一种方法去除我们不需要的指令。可以运用类似编译原理中常量传播的思想，追踪所有与输入数据相关的数据位置，dump一份只和输入相关的指令：

```python
with open(&#34;chal.txt&#34;, &#34;r&#34;) as rf:
	x = &#39; &#39;.join([y.strip(&#39;\n&#39;) for y in rf.readlines()])
buf = [int(y) for y in x[:-1].split(&#39; &#39;)]
input_pos = []
i = 0
input_flag = &#34;hitcon{r\n&#34;
input_pos = [i for i in range(16, 16&#43;8, 1)]
what_buf = &#34;&#34;
j = 0
while i &gt;= 0:
	a1 = buf[i]
	a2 = buf[i&#43;1]
	a3 = buf[i&#43;2]
	if a1 &lt; 0:
		what_buf &#43;= f&#34;INPUT TO [{a2}](origin:{buf[a2]}), dest {a3}\n&#34;
		buf[a2] -= -ord(input_flag[j])
		j &#43;= 1
		if buf[a2] &gt; 0:
			i &#43;= 3
		else:
			i = a3
		i = a3
	if a2 &lt; 0:
		what_buf &#43;= f&#34;OUTPUT [{a1}]{chr(buf[a1])}, dest {a3}\n&#34;
		if chr(buf[a1]) == &#39;!&#39;:
			for i in range(16, 16&#43;21, 1):
				print(buf[i], end=&#34; &#34;)
		i = a3

	if a1 &gt;= 0 and a2 &gt;= 0:
		if a1 not in input_pos and a2 not in input_pos:
			buf[a2] -= buf[a1]
			if buf[a2] &lt;= 0:
				i = a3
			else:
				i &#43;= 3
		else:
			what_buf &#43;= f&#34;INPUT RELATED: buf[{a2}] -= buf[{a1}](origin:buf[{a1}]={buf[a1]},buf[{a2}]={buf[a2]})\n&#34;
			if a1 in input_pos and a2 not in input_pos:
				input_pos.append(a2)
			buf[a2] -= buf[a1]
			if buf[a2] == 0 and a2 not in range(16, 16&#43;8, 1):
				#print(f&#34;[{a2}] is considered a constraint&#34;)
				what_buf &#43;= f&#34;[{a2}] is considered a constraint\n&#34;
				input_pos.remove(a2)
			if buf[a2] &gt; 0:
				i &#43;= 3
			else:
				i = a3
with open(&#34;log.txt&#34;, &#34;w&#34;) as f:
	f.write(what_buf)
print(&#34;&#34;)
print(len(what_buf))
```

上面的代码是经过多次逆向和修改后的最终代码，range(16, 16&#43;8, 1)是在dump指令得出输入数据存储位置之后加上的，这个定位和上面追踪输入的思路类似。

需要注意的是，可以发现对buf[0]~buf[4]的操作非常多，不难发现他们是寄存器类似用途的内存，所以当这部分数据等于0时可以认定它们不再与输入有关并且停止追踪。这样可以dump出一份相对短的代码。

从这段字节码可以看出只涉及简单的加减操作（本来以为有用减法实现其他运算的骚操作），那么最后的算法一定是一个多项式或矩阵。

观察并打印一下算法结束后的buf数组，可以观察到输入位置的数据发生了变化，可以推测加密后的数据是存在原地的。

接下来手动fuzz一下，看看变动输入数据发生的变化。首先以`hitcon{test_flag}`为例dump一份加密数据，改为`hitcon{sest_flag}`再dump一份加密数据，可以发现只有前8位发生了变化，结合诸多类似方式的验证可以知道flag验证为8位一组。

顺便某一次得到的密文是[16774156, 1396, 16776307, 3691, 1558, 6506, 2587, 10]，由于flag开头`hitcon{`就占了7位，所以此时得到的密文一定和正确密文相差不大，在chal.txt里面寻找类似的东西，可以找到密文（就在输入数据和输出的字符串中间，肯定没问题）

```
cip = [16774200, 1411, 16776275, 3646, 1532, 6451, 2510, 16777141, 16775256, 2061, 16776706, 2260, 2107, 6124, 878, 16776140, 16775299, 1374, 16776956, 2212, 1577, 4993, 1351, 16777040, 16774665, 1498, 16776379, 3062, 1593, 5966, 1924, 16776815, 16774318, 851, 16775763, 3663, 711, 5193, 2591, 16777069, 16774005, 1189, 16776283, 3892, 1372, 6362, 2910, 307, 16775169, 1031, 16776798, 2426, 1171, 4570, 1728, 33, 16775201, 819, 16776898, 2370, 1132, 4255, 1900, 347]
```

得到正确密文之后，由于flag开头只剩一位，可以手动爆破一下知道flag的前8位是`hitcon{r`

有了一组flag，结合前面加密算法为矩阵方程组的推测，可以直接弄出矩阵的系数。具体来说，对每一位依次加一，例如传入`iitcon{r`，那么得到的密文和正确密文的差值便是该项在该方程中的系数。

顺便由于1677....是2^24，简单猜测一下那个是负数标记。

```python
def execute(input_flag, nowpos):
	with open(&#34;chal.txt&#34;, &#34;r&#34;) as rf:
		x = &#39; &#39;.join([y.strip(&#39;\n&#39;) for y in rf.readlines()])
	buf = [int(y) for y in x[:-1].split(&#39; &#39;)]
	input_pos = []
	i = 0
	input_pos = [i for i in range(16, 16&#43;8, 1)]
	what_buf = &#34;&#34;
	j = 0
	calres = 0
	while i &gt;= 0:
		a1 = buf[i]
		a2 = buf[i&#43;1]
		a3 = buf[i&#43;2]
		if a1 &lt; 0:
			what_buf &#43;= f&#34;INPUT TO [{a2}](origin:{buf[a2]}), dest {a3}\n&#34;
			buf[a2] -= -ord(input_flag[j])
			j &#43;= 1
			if buf[a2] &gt; 0:
				i &#43;= 3
			else:
				i = a3
			i = a3
		if a2 &lt; 0:
			what_buf &#43;= f&#34;OUTPUT [{a1}]{chr(buf[a1])}, dest {a3}\n&#34;
			if chr(buf[a1]) == &#39;!&#39;:
				#print(buf[16:16&#43;8])
				return buf[16&#43;nowpos]
			i = a3

		if a1 &gt;= 0 and a2 &gt;= 0:
			if a1 not in input_pos and a2 not in input_pos:
				buf[a2] -= buf[a1]
				if buf[a2] &lt;= 0:
					i = a3
				else:
					i &#43;= 3
			else:
				what_buf &#43;= f&#34;INPUT RELATED: buf[{a2}] -= buf[{a1}](origin:buf[{a1}]={buf[a1]},buf[{a2}]={buf[a2]})\n&#34;
				if a1 in input_pos and a2 not in input_pos:
					input_pos.append(a2)
				buf[a2] -= buf[a1]
				if buf[a2] == 0 and a2 not in range(16, 16&#43;8, 1):
					#print(f&#34;[{a2}] is considered a constraint&#34;)
					what_buf &#43;= f&#34;[{a2}] is considered a constraint\n&#34;
					input_pos.remove(a2)
				if buf[a2] &gt; 0:
					i &#43;= 3
				else:
					i = a3

ori_flag = &#34;hitcon{r\n&#34;
targetres = [16774200, 1411, 16776275, 3646, 1532, 6451, 2510, 16777141]
matrix = []
for pos in range(8):
	xi = []
	for j in range(8):
		inpflag = ori_flag[:j]&#43;chr(ord(ori_flag[j])&#43;1)&#43;ori_flag[j&#43;1:]
		#print(inpflag)
		calres = execute(inpflag, pos)
		xi.append(calres-targetres[pos])
	#print(xi)
	matrix.append(xi)
print(matrix)
```

得到矩阵系数，z3一下就解决了。

```python
from z3 import *
matrix = [[-7, -2, 3, -4, 4, -13, -2, -7],
[-2, 3, 2, 5, 6, -10, 11, -3],
[-2, -4, -3, -3, 4, -5, -2, 6],
[9, 3, -3, 5, -6, 17, 2, 7],
[-2, 2, -1, 3, 6, -8, 9, 4],
[6, 7, -2, 13, 5, 1, 20, 8],
[9, -1, -6, 1, -8, 22, -6, 13],
[5, -5, -8, -6, -5, 15, -11, 15]]
cip = [16774200, 1411, 16776275, 3646, 1532, 6451, 2510, 16777141, 16775256, 2061, 16776706, 2260, 2107, 6124, 878, 16776140, 16775299, 1374, 16776956, 2212, 1577, 4993, 1351, 16777040, 16774665, 1498, 16776379, 3062, 1593, 5966, 1924, 16776815, 16774318, 851, 16775763, 3663, 711, 5193, 2591, 16777069, 16774005, 1189, 16776283, 3892, 1372, 6362, 2910, 307, 16775169, 1031, 16776798, 2426, 1171, 4570, 1728, 33, 16775201, 819, 16776898, 2370, 1132, 4255, 1900, 347]
for i in range(len(cip)):
	if cip[i] &gt; 16770000:
		cip[i] -= 16777216
solver = Solver()
flag = [Int(f&#34;x{i}&#34;) for i in range(64)]
res = [0 for i in range(64)]
for k in range(8):
	for i in range(8):
		for j in range(8):
			res[k*8&#43;i] &#43;= flag[k*8&#43;j]*matrix[i][j]
		solver.add(res[k*8&#43;i] == cip[k*8&#43;i])

solver.check()
get_flag = solver.model()
for i in range(64):
	print(chr(get_flag[flag[i]].as_long()), end = &#34;&#34;)
```

## CrazyArcade 

给了一个泡泡堂游戏和一个驱动，简单找一下 WIN 逻辑

```c&#43;&#43;
  if ( (unsigned int)dword_7FF63A836238 &lt; 0x1337 )
  {
    v6 = 5i64;
    v7 = &#34;PAUSE&#34;;
  }
  else
  {
    v6 = 3i64;
    v7 = &#34;WIN&#34;;
  }
```

要求 dword_7FF63A836238 &gt;= 0x1337 查引用

```c&#43;&#43;
int __fastcall sub_7FF63A8230A0(__int64 a1)
{
  int *v2; // rax
  unsigned int v3; // ecx
  DWORD lpBytesReturned[2]; // [rsp&#43;40h] [rbp-88h] BYREF
  DWORD BytesReturned; // [rsp&#43;48h] [rbp-80h] BYREF
  __int64 OutBuffer[3]; // [rsp&#43;50h] [rbp-78h] BYREF
  int v8; // [rsp&#43;68h] [rbp-60h]
  __int128 v9; // [rsp&#43;6Ch] [rbp-5Ch]
  int v10; // [rsp&#43;7Ch] [rbp-4Ch]
  __int64 InBuffer[3]; // [rsp&#43;80h] [rbp-48h] BYREF
  int v12; // [rsp&#43;98h] [rbp-30h]
  int v13; // [rsp&#43;9Ch] [rbp-2Ch]
  __int128 v14; // [rsp&#43;A0h] [rbp-28h]

  sub_7FF63A823850(a1, lpBytesReturned);
  v2 = dword_7FF63A8362E0;
  if ( dword_7FF63A8362E0[15 * lpBytesReturned[1] &#43; lpBytesReturned[0]] == 5 )
  {
    if ( byte_7FF63A834038 )
      LODWORD(v2) = Mix_PlayChannel(1i64, qword_7FF63A8362D0, 0i64);
    v3 = dword_7FF63A836238;
    *(_BYTE *)(a1 &#43; 20) = 1;
    if ( v3 &lt; 4919 )
    {
      v8 = 1;
      OutBuffer[0] = 0i64;
      v9 = 0i64;
      OutBuffer[2] = 0i64;
      v10 = 0;
      OutBuffer[1] = qword_7FF63A836240 &#43; 12288 &#43; v3 % 0x25;
      DeviceIoControl(hDevice, 0x80002048, OutBuffer, 0x30u, OutBuffer, 0x30u, &amp;BytesReturned, 0i64);
      v14 = 0i64;
      InBuffer[0] = 0i64;
      InBuffer[2] = 0i64;
      v12 = 1;
      InBuffer[1] = dword_7FF63A836238 % 0x25u &#43; qword_7FF63A836240 &#43; 12288;
      v13 = (unsigned __int8)(dword_7FF63A836238 ^ v9) ^ *(unsigned __int8 *)(dword_7FF63A836238 % 0x584u
                                                                            &#43; qword_7FF63A836248);
      LODWORD(v2) = DeviceIoControl(hDevice, 0x8000204C, InBuffer, 0x30u, InBuffer, 0x30u, lpBytesReturned, 0i64);
      &#43;&#43;dword_7FF63A836238;
    }
  }
  return (int)v2;
}
```

尝试触发这个`&#43;&#43;dword_7FF63A836238`，直接patch掉`if ( dword_7FF63A8362E0[15 * lpBytesReturned[1] &#43; lpBytesReturned[0]] == 5 )`的条件变成不等于。

启动游戏发现一开始敌人全死了，Cheat Engine看dword_7FF63A836238变成了4（一共4个敌人）

不小心玩死了自己 GameOver 重来发现 dword_7FF63A836238 变成了 8，可以发现重来之后这个计数不清零。

写个脚本重复炸死自己（这里patch后敌人会被开局杀），挂亿会之后cheat engine在内存里搜hitcon得到flag。

感觉非预期了，开题到出解题思路不到十分钟

## Full Chain - The Blade

逻辑在 `verify` 函数，打乱&#43;逐位数字计算，不用逆直接动调打表就行。

```python
src = &#39;abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{_&#39;
dst = &#39;Rp5v{AZmM8XWy1sgNhTB_oCzYVdPrGn6KD3Q9lke4qtFxHb0uUOcS2jIEJfL7aiw&#39;
table = []
for x in dst:
    table.append(src.index(x))

rtable = []
for x in src:
    rtable.append(dst.index(x))

#print(rtable)

sub_table = [
    0xfb,0x7b,0x4e,0xbb,0x51,0x15,0x8d,0xdb,
    0xb0,0xac,0xa5,0x8e,0xaa,0xb2,0x60,0xeb,
    0x63,0x5c,0xde,0x42,0x2b,0xc6,0xa6,0x35,
    0x30,0x43,0xd6,0x5f,0xbd,0x24,0xb1,0xe3,
    0x8c,0xa7,0xd5,0x2a,0x7c,0x6d,0x8b,0x17,
    0x9d,0x83,0xfe,0x69,0x10,0x59,0xa9,0x9e,
    0x0f,0x1c,0x66,0x97,0x5b,0x61,0xed,0xad,
    0xe0,0xda,0x27,0x06,0x25,0xdc,0x5e,0xe7,
    0x41,0x32,0xd2,0xd9,0x8f,0xee,0xaf,0x03,
    0x93,0x3a,0x00,0xa2,0xe1,0xb3,0xec,0x81,
    0x9f,0xca,0x58,0xb7,0x79,0xfd,0x3b,0xa0,
    0x02,0x0c,0xcb,0xa8,0x80,0xc0,0x16,0x4d,
    0x2f,0x75,0x71,0x0a,0x04,0x39,0xff,0xc1,
    0x9c,0xab,0xef,0xa4,0xd8,0xe2,0x14,0xc2,
    0x6c,0x64,0x1e,0x6b,0x7e,0x99,0x2e,0x09,
    0x0b,0x86,0x74,0x6a,0xc4,0x2d,0x4f,0xf9,
    0xfa,0x94,0xb6,0x1f,0x89,0x6f,0x5d,0xe8,
    0xea,0xb5,0x5a,0x65,0x88,0xc5,0x7f,0x77,
    0x11,0xcf,0xf1,0x1b,0x3f,0xf4,0x48,0x47,
    0x12,0xe4,0xba,0xdf,0xe9,0x62,0x6e,0xb4,
    0x96,0xcd,0x13,0x53,0x4b,0x28,0xd7,0xd1,
    0x33,0xb8,0xe6,0x7a,0x2c,0x9b,0x29,0x44,
    0x52,0xf7,0x20,0xf2,0x31,0xd3,0xb9,0x40,
    0xd0,0x34,0xf5,0x54,0x1a,0x01,0xa1,0x92,
    0xfc,0x85,0x07,0xbe,0xdd,0xbc,0x19,0xf3,
    0x36,0xf6,0x72,0x98,0x4c,0x7d,0xc7,0xd4,
    0x45,0x4a,0x9a,0xc3,0x8a,0xe5,0x50,0x46,
    0xcc,0x68,0x76,0x67,0xc9,0x0e,0x3c,0x57,
    0xf0,0x22,0xbf,0x26,0x84,0x0d,0x90,0xa3,
    0xae,0x3d,0x1d,0xc8,0x91,0x05,0x87,0x70,
    0x08,0x73,0x21,0x49,0x55,0x3e,0x37,0x23,
    0x18,0x56,0xce,0x82,0x38,0x95,0x78,0xf8,
]

correct = [0xA7, 0x51, 0x68, 0x52, 0x85, 0x27, 0xFF, 0x31, 0x88, 0x87, 
  0xD2, 0xC7, 0xD3, 0x23, 0x3F, 0x52, 0x55, 0x10, 0x1F, 0xAF, 
  0x27, 0xF0, 0x94, 0x5C, 0xCD, 0x3F, 0x7A, 0x79, 0x9F, 0x2F, 
  0xF0, 0xE7, 0x45, 0xF0, 0x86, 0x3C, 0xF9, 0xB0, 0xEA, 0x6D, 
  0x90, 0x42, 0xF7, 0x91, 0xED, 0x3A, 0x9A, 0x7C, 0x01, 0x6B, 
  0x84, 0xDC, 0x6C, 0xC8, 0x43, 0x07, 0x5C, 0x08, 0xF7, 0xDF, 
  0xEB, 0xE3, 0xAE, 0xA4
]

&#39;&#39;&#39;
correct = [0xc3,0xba,0x14,0x69,0x6c,0xe0,0x2a,0x97,
0x2b,0x3d,0xee,0x1d,0x09,0xca,0x67,0x01,
0x7a,0xfa,0xbd,0x0e,0x7e,0xae,0x50,0x5b,
0x26,0x66,0xfc,0xd3,0x62,0x88,0x68,0x20,
0x0a,0x13,0xe4,0xc2,0x6a,0x9a,0x78,0xa8,
0x15,0xd7,0x3b,0x23,0x53,0x9d,0xb9,0x52,
0xcb,0xd9,0xfb,0x55,0x86,0x92,0xf6,0x10,
0x38,0xe9,0xec,0xbe,0xa4,0x87,0x36,0x12,
]
&#39;&#39;&#39;

flag = list(correct)

for i in range(256):
    f = []
    for j in range(64):
        f.append(sub_table.index(flag[j]))
    flag = list(f)
    f = []
    for i in range(64):
        f.append(flag[rtable[i]])
    flag = list(f)
    #print(flag)
print(flag)
for _ in flag:
    print(chr(_), end=&#34;&#34;)
```

发现不对，看了一下发现没有比较逻辑，反而是把flag和密文填到了某个东西里，一看是一段shellcode。F5一下

```c&#43;&#43;
v21 = &#39;hs/nib/&#39;;
  v2 = sys_open((const char *)&amp;v21, 0, 0);
  v3 = v2;
  v20[2] = 0;
  v4 = sys_read(v2, (char *)&amp;v20[2], 4uLL);
  v5 = v20[2];
  v6 = sys_close(v3);
  v20[3] = &#39;\0&#39;;
  strcpy((char *)v20, &#34;/etc/passwd&#34;);
  v7 = sys_open((const char *)v20, 0, 0);
  v8 = v7;
  *(_DWORD *)&amp;v18[8] = 0;
  v9 = sys_read(v7, &amp;v18[8], 4uLL);
  v10 = *(_DWORD *)&amp;v18[8];
  v11 = sys_close(v8);
  *(_WORD *)&amp;v18[&#39;\n&#39;] = &#39;\0&#39;;
  v19 = &#39;\0&#39;;
  strcpy(v18, &#34;/dev/zero&#34;);
  v12 = sys_open(v18, 0, 0);
  v17 = 0LL;
  v13 = sys_read(v12, (char *)&amp;v17, 4uLL);
  v14 = ((unsigned __int64)~v17 &gt;&gt; 29) / (unsigned __int128)0x29uLL;
  v15 = sys_close(v12);
  v17 = ((unsigned int)v14 ^ ~__ROR4__(v10 ^ (v5 - 559038737), 11)) == 0xDEADBEEF;
  v16 = sys_write(v0, (const char *)&amp;v17, 8uLL);
```

这里面关键的几个数据 

v5 从/bin/sh读入4个字节 `\x7fELF`

v10 从/etc/passwd读入4个字节` root`

v14 读/dev/null/得0，然后计算一下

小逆一下就结束了

```python
src = &#39;abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{_&#39;
dst = &#39;Rp5v{AZmM8XWy1sgNhTB_oCzYVdPrGn6KD3Q9lke4qtFxHb0uUOcS2jIEJfL7aiw&#39;
table = []
for x in dst:
    table.append(src.index(x))

rtable = []
for x in src:
    rtable.append(dst.index(x))

sub_table = [
    0xfb,0x7b,0x4e,0xbb,0x51,0x15,0x8d,0xdb,
    0xb0,0xac,0xa5,0x8e,0xaa,0xb2,0x60,0xeb,
    0x63,0x5c,0xde,0x42,0x2b,0xc6,0xa6,0x35,
    0x30,0x43,0xd6,0x5f,0xbd,0x24,0xb1,0xe3,
    0x8c,0xa7,0xd5,0x2a,0x7c,0x6d,0x8b,0x17,
    0x9d,0x83,0xfe,0x69,0x10,0x59,0xa9,0x9e,
    0x0f,0x1c,0x66,0x97,0x5b,0x61,0xed,0xad,
    0xe0,0xda,0x27,0x06,0x25,0xdc,0x5e,0xe7,
    0x41,0x32,0xd2,0xd9,0x8f,0xee,0xaf,0x03,
    0x93,0x3a,0x00,0xa2,0xe1,0xb3,0xec,0x81,
    0x9f,0xca,0x58,0xb7,0x79,0xfd,0x3b,0xa0,
    0x02,0x0c,0xcb,0xa8,0x80,0xc0,0x16,0x4d,
    0x2f,0x75,0x71,0x0a,0x04,0x39,0xff,0xc1,
    0x9c,0xab,0xef,0xa4,0xd8,0xe2,0x14,0xc2,
    0x6c,0x64,0x1e,0x6b,0x7e,0x99,0x2e,0x09,
    0x0b,0x86,0x74,0x6a,0xc4,0x2d,0x4f,0xf9,
    0xfa,0x94,0xb6,0x1f,0x89,0x6f,0x5d,0xe8,
    0xea,0xb5,0x5a,0x65,0x88,0xc5,0x7f,0x77,
    0x11,0xcf,0xf1,0x1b,0x3f,0xf4,0x48,0x47,
    0x12,0xe4,0xba,0xdf,0xe9,0x62,0x6e,0xb4,
    0x96,0xcd,0x13,0x53,0x4b,0x28,0xd7,0xd1,
    0x33,0xb8,0xe6,0x7a,0x2c,0x9b,0x29,0x44,
    0x52,0xf7,0x20,0xf2,0x31,0xd3,0xb9,0x40,
    0xd0,0x34,0xf5,0x54,0x1a,0x01,0xa1,0x92,
    0xfc,0x85,0x07,0xbe,0xdd,0xbc,0x19,0xf3,
    0x36,0xf6,0x72,0x98,0x4c,0x7d,0xc7,0xd4,
    0x45,0x4a,0x9a,0xc3,0x8a,0xe5,0x50,0x46,
    0xcc,0x68,0x76,0x67,0xc9,0x0e,0x3c,0x57,
    0xf0,0x22,0xbf,0x26,0x84,0x0d,0x90,0xa3,
    0xae,0x3d,0x1d,0xc8,0x91,0x05,0x87,0x70,
    0x08,0x73,0x21,0x49,0x55,0x3e,0x37,0x23,
    0x18,0x56,0xce,0x82,0x38,0x95,0x78,0xf8,
]

correct = [0xA7, 0x51, 0x68, 0x52, 0x85, 0x27, 0xFF, 0x31, 0x88, 0x87, 
  0xD2, 0xC7, 0xD3, 0x23, 0x3F, 0x52, 0x55, 0x10, 0x1F, 0xAF, 
  0x27, 0xF0, 0x94, 0x5C, 0xCD, 0x3F, 0x7A, 0x79, 0x9F, 0x2F, 
  0xF0, 0xE7, 0x45, 0xF0, 0x86, 0x3C, 0xF9, 0xB0, 0xEA, 0x6D, 
  0x90, 0x42, 0xF7, 0x91, 0xED, 0x3A, 0x9A, 0x7C, 0x01, 0x6B, 
  0x84, 0xDC, 0x6C, 0xC8, 0x43, 0x07, 0x5C, 0x08, 0xF7, 0xDF, 
  0xEB, 0xE3, 0xAE, 0xA4
]


def disror(x, cnt):
    return ((x &gt;&gt; (32-cnt)) | (x &lt;&lt; cnt)) &amp; 0xFFFFFFFF
def distrans(x):
    x1 = &#39;\x7fELF&#39;
    x2 = &#39;root&#39;
    x3 = (0xFFFFFFFFFFFFFFFF &gt;&gt; 29) // 0x29
    x1 = ord(x1[0]) &#43; (ord(x1[1]) &lt;&lt; 8) &#43; (ord(x1[2]) &lt;&lt; 16) &#43; (ord(x1[3]) &lt;&lt; 24)
    x2 = ord(x2[0]) &#43; (ord(x2[1]) &lt;&lt; 8) &#43; (ord(x2[2]) &lt;&lt; 16) &#43; (ord(x2[3]) &lt;&lt; 24)
    x ^= x3
    x = ~x &amp; 0xFFFFFFFF
    x = disror(x, 11)
    x ^= x2
    x -= x1
    return x


for i in range(0, len(correct), 4):
    x = correct[i] &#43; (correct[i&#43;1] &lt;&lt; 8) &#43; (correct[i&#43;2] &lt;&lt; 16) &#43; (correct[i&#43;3] &lt;&lt; 24)
    x = distrans(x)
    correct[i&#43;3] = (x &gt;&gt; 24) &amp; 0xFF
    correct[i&#43;2] = (x &gt;&gt; 16) &amp; 0xFF
    correct[i&#43;1] = (x &gt;&gt; 8) &amp; 0xFF
    correct[i] = (x) &amp; 0xFF

print(correct)

flag = list(correct)

for i in range(256):
    f = []
    for j in range(64):
        f.append(sub_table.index(flag[j]))
    flag = list(f)
    f = []
    for i in range(64):
        f.append(flag[rtable[i]])
    flag = list(f)
print(flag)
for _ in flag:
    print(chr(_), end=&#34;&#34;)
```

## 总结

感觉这几个题里就LessEQaulmore需要小看一会吧，如果明天还有题我再来写（如果文章发布的时候你看到了这句话说明我没写）


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/hitcon2023/  

