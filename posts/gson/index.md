# SCTF2023 - SycGson


打开看到 Golang 字样，使用 go_parser 恢复一下符号。

https://github.com/0xjiayu/go_parser

```c&#43;&#43;
 v24 = &#34;115.239.215.75&#34;;
  v25 = 14LL;
  v26 = &#34;12345&#34;;
  v27 = 5LL;
  *((_QWORD *)&amp;v2 &#43; 1) = 2LL;
  v7 = os_exec_Command();
  v12 = os_exec__Cmd_StdoutPipe(v7);
```

奇妙的逻辑，可以通过字符串判断是 nc 取数据，`nc 115.239.215.75 12345` 看一眼拿到的数据，形式如下：

```c&#43;&#43;
{1801 
[
{1878 1630 {1600 1047 1355}} 
{1968 1923 {1602 1096 1287}} 
{1805 1572 {1600 1102 1283}} 
{1963 1669 {1600 1165 1327}}] 
4}
```

看数据 parse 逻辑，从.rodata段残留的结构体信息恢复结构体：

```go
struct City {
	Name: int;
	Neighbours: []NeighbourCity;
	Delta: uint8
}
struct NeighbourCity {
    Name: int;
    Distance: int;
    Cost: Cost;
}
struct Cost {
    Transportation: int;
    Time: int;
    Expense: int;
}
```

看 FindPath 逻辑，简单易懂，每次选一个 NeighborCity，加上Distance，减去 Transportation， 异或 Time，乘上 Expense，加上点 Delta，找一条五种权重都满足约束的路径。

输入和选择的路对应的关系有点玄学，动调一下也不难发现是第一组对应`fedc`第二组对应`ba98`以此类推，所以只需要从起点 2 开始找到一条到终点 1986 的满足条件的路径就行了。

直接搜复杂度不对，注意到 Transportation 都大于等于 1600，而要求的约束正好是100000 - 1600*31，所以只有 Transportation 为 1600 的路径可以使用。

赛场上没看到这个调了一整天，我但凡睁开眼睛看看早就做完了，给 cnss 的民那谢罪了。

```python
x = [#数据 ]
p = 0
a = [[] for i in range(200)]
o = []
i = 0
axor = [[] for i in range(200)]
asub = [[] for i in range(200)]
amul = [[] for i in range(200)]
aadd = [[] for i in range(200)]
while p &lt; len(x):
	a[i].append(x[p&#43;1]-1800)
	a[i].append(x[p&#43;6]-1800)
	a[i].append(x[p&#43;11]-1800)
	a[i].append(x[p&#43;16]-1800)

	aadd[i].append(x[p&#43;2])
	aadd[i].append(x[p&#43;7])
	aadd[i].append(x[p&#43;12])
	aadd[i].append(x[p&#43;17])

	asub[i].append(x[p&#43;3])
	asub[i].append(x[p&#43;8])
	asub[i].append(x[p&#43;13])
	asub[i].append(x[p&#43;18])

	axor[i].append(x[p&#43;4])
	axor[i].append(x[p&#43;9])
	axor[i].append(x[p&#43;14])
	axor[i].append(x[p&#43;19])

	amul[i].append(x[p&#43;5])
	amul[i].append(x[p&#43;10])
	amul[i].append(x[p&#43;15])
	amul[i].append(x[p&#43;20])

	o.append(x[p&#43;21])
	p &#43;= 22
	i &#43;= 1

order = []
for i in range(200):
	order.append([0, 1, 2, 3])
	for k in range(4):
		for j in range(3):
			if aadd[i][order[i][j]] &lt; aadd[i][order[i][j&#43;1]]:
				tmp = order[i][j]
				order[i][j] = order[i][j&#43;1]
				order[i][j&#43;1] = tmp


st = 2
fi = 186
vis = [0 for i in range(200)]
pre = [-1 for i in range(200)]

def dfs(u, dep, xx, xorsum, subsum, mulsum, addsum):
	vis[u] = 1
	if dep == 31:
		if u == fi and mulsum == 0xAA000000 and addsum == 0xD898 and subsum == 0xC4E0 and xorsum == 0x3D0 and xx == 131:
			print(&#34;%x&#34;%mulsum)
			print(&#34;%x&#34;%addsum)
			print(&#34;%x&#34;%subsum)
			print(&#34;%x&#34;%xorsum)
			print(&#34;Solved&#34;)
			return 1
		return 0
	if subsum &lt; 0xC4E0:
		return 0
	if addsum &gt; 0xD898:
		return 0
	if xx &gt; 131:
		return 0
	for i in range(4):
		v = a[u][i]
		if asub[u][i] != 1600:
			continue
		if vis[v] == 0:
			vis[v] = 1
			if dfs(v, dep&#43;1, xx&#43;o[u], xorsum^axor[u][i], subsum-asub[u][i], (mulsum*amul[u][i])&amp;0xFFFFFFFF, addsum&#43;aadd[u][i]) == 1:
				print(u, end=&#34;, &#34;)
				return 1
			vis[v] = 0
	vis[u] = 0
	return 0
vis[st] = 1
dfs(st, 0, 0, 0, 100000, 1, 0)
lis = [186, 187, 188, 189, 190, 191, 172, 153, 134, 114, 94, 74, 53, 32, 11, 10, 29, 48, 68, 88, 107, 126, 145, 144, 143, 122, 101, 80, 60, 40, 21, 2]
i = len(lis)-1
print(&#34;&#34;)
nowp = 0
table = &#34;fedcba9876543210&#34;
while i &gt; 0:
	n = -1
	for j in range(4):
		if a[lis[i]][j] == lis[i-1]:
			n = j
			break
	if n == -1:
		print(&#34;panic&#34;)
	print(table[nowp&#43;n], end=&#34;&#34;)
	nowp &#43;= 4
	nowp %= 16
	i -= 1

```

`SCTF{db61f852f960da71c873e950e952c97}`


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/gson/  

