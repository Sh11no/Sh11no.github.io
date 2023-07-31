# ciscn2023-Pwsh Powershell反混淆对抗实战


###  碎碎念

​		刚进黑灯模式就出了flag，看到还是 0 解题以为可以拿全场唯一解光荣退役了，结果平台的flag配置是烂的，以为 0 解的原因是平台烂直接找运维对线，拉扯了一个小时左右赛后说 pwsh 需要人工验证flag以为其实大家都会做只是没交上，第二天起床一看还真是一血全场只有 2 解。也算光荣退役了？

![](https://small.fileditch.ch/s3/ANqyDJIGowcAvMtJnIon.png)

但是比赛结果一般，打ctf不如闲鱼买flag，整场比赛充斥着国粹这种脑瘫题，不过打不过闲鱼哥还是我太菜了。

### Writeups

#### 初步分析

题目备份：https://small.fileditch.ch/s3/ssQpUZIxaIRvkfVeChBp.ps1

一个`powershell`脚本，先base64后解密再执行，先上手解密base64串

```python
with open("p4.ps1", "w") as f:
	f.write(base64.b64decode(code).decode())
```

```powershell
$M=@{129693309641433576095262078804193086780='(New-ObJecT sysTEm.Io.COMpResSIoN.DEflATesTReAm( [SyStEM.iO.meMORYsTreaM] [sYSTEm.CoNVErT]::FRoMbASe64StrIng( "1VhNaxxHED3Xv+iDYXZBWuwEArHJwQYTy8gS2CKHiCUHIX/koDiKyMXWf89G8s7Ux6ue7hpN7zqBZKa7qvrVq1fVs+rSt3/o7j/0/wNtH+5eaLt7/ySWktmmbThuTP06bfe1pY0grNUi9fY6tPHOBLYnkec17FuLnpHEY2RyVgsqS5T0kLM+yiyA4CTXSa3yOoO4EoWLS+U6mjtxF2K75DKYVx5LkgBWtpCjUBYE+GdMvFpoCXFswiShhd3ABXQR9mqKxxdje1RGgPmqqWXTICCR7fTEbe1HV7FJv+2yAUYpYq2Pjj....'
$t=Read-Host -Prompt "Enter your flag";
[System.Collections.Queue]$tt=([byte[]][char[]]$t|%{$_ -shr 4;$_%16});
iex($M[129693309641433576095262078804193086780])
```

M太长了这里就不放了，可以看到M是一个字典，对应的是混淆过的powershell脚本，每个`key`(一串数字)分别对应了一段混淆过的powershell的脚本，尝试解混淆。

#### 混淆分析

混淆方式类似如下，这里给出几个样本：

```powershell
(New-ObJecT sysTEm.Io.COMpResSIoN.DEflATesTReAm( [SyStEM.iO.meMORYsTreaM] [sYSTEm.CoNVErT]::FRoMbASe64StrIng( "....." ) ,[SYSTeM.io.COMpRESSIoN.COmPressiOnmODe]::dECoMprEss ) | FoREaCH-objEct{New-ObJecT  sySTem.Io.StReamreAder( $_ , [TexT.enCOdING]::ascII) }|FOrEacH-obJECt{$_.REAdtoend( )} )|. ( $sHElLId[1]+$Shellid[13]+"X"); 

&( $SHEllID[1]+$SHEllid[13]+"X") ( nEw-obJEcT  System.io.STREAMrEADeR((nEw-obJEcT  IO.cOMPreSsiOn.deFLaTeSTreAm([system.io.MeMoRYStReam][sYsTem.COnVERt]::fROMBAsE64sTRiNG(" ...") ,

[sYsTEm.io.COmPREsSIoN.coMpRessionmoDE]::deComPResS )|% { nEw-objEcT iO.StREamREAdEr( $_ ,[TExt.EncOdING]::asCii )}|%{ $_.ReadtoeND( ) })|& ( $EnV:cOMspEc[4,15,25]-joiN""); 

( New-OBjecT  system.iO.STreAmReAdeR(( New-OBjecT SYstEM.IO.cOMprESsion.DeFlATeStrEAm( [io.meMOrySTReAm][cONVert]::FrOmBASE64sTrInG( "..."),[SysTEm.IO.coMPreSsIon.coMpreSsIonMODE]::decOmPress )),[sYsTeM.TEXT.ENcOdiNg]::aSciI) ).REAdtoeND()| .( $pShOmE[21]+$pShoME[34]+"x");
```

可以归纳为以下的模式：

- `iex的变种` (`混淆过的字符串和对应的解密代码`)
- `混淆过的字符串和对应的解密代码` | `iex的变种`

其中 iex 是 powershell 的一个 cmdlet 指令，全名 `Invoke-Expression` ，作用是执行表达式（类似`eval()`）。

在上面的例子中，混淆过的字符串和对应的解密代码都是base64和压缩，但在嵌套的更深层次的混淆中，存在很多种加密或编码方式。

而`iex`的变种是如下几种：

```
( $SHEllID[1]+$SHEllid[13]+"X")
( $EnV:cOMspEc[4,15,25]-joiN"")
.( $pShOmE[21]+$pShoME[34]+"x")
```

在嵌套的更深层次的混淆中同样存在非常多种iex的变种，这里只是其中几种。

（除此之外还有随机大小写混淆但是不关注）

#### 静态解混淆尝试

一个直观的思路是去掉代码中的iex变种变成字符串解密操作，直接运行得到解密后的代码。但是混淆后的代码多达1000+个，每个都有5~6层混淆嵌套，手动非常的不现实。

本来想当正则大师解决，但是iex变种有20+种难以收集，且存在混淆，执行方式也不一样。

另外这里有个对本题没有帮助的仓库。https://github.com/pan-unit42/public_tools/tree/master/powershellprofiler

#### 动态解混淆

​		很明显我们的目的是找到一种自动化解混淆的方式。如果我们不考虑静态分析，而是考虑 Hook Powershell里的`iex`函数，让它每次被调用的时候都改为输出参数的值然后直接运行脚本呢？

查一查可以找到在`Powershell`中命令默认的调用顺序：

1. Alias
2. Function
3. Cmdlet
4. 本机 Windows 命令

Powershell 会按照上面的顺序寻找，并且调用第一个被寻找到的方法

可以发现，对 Function 的调用优先于 Cmdlet。也就是说如果我们定义一个名为`Invoke-Expression`的函数，在`iex`被调用时将会调用我们的自定义函数而不是`iex`。

编写如下函数重载`iex`.

```powershell
function Invoke-Expression{$input|%{$_;};$args|%{$_;}};
```

作用是将`input`（用于管道执行方法）或`args`（用于调用执行方法）直接输出。

现在我们可以自动化解混淆，请一个 `python` 大师来完成。

注意到代码中包含一些干扰直接执行的代码比如`while($true){echo Warning!};`和`(sleep 10000);`会导致程序卡死，但是情况不多（就这两种）特判一下即可。

Script by [Timlzh](https://www.cnblogs.com/timlzh/)

```python
import subprocess
from threading import Thread
from json import loads, dumps
with open('hash.json', 'r') as f:
    hash_dict = eval(f.read())

redir = "function Invoke-Expression{$input|%{$_;};$args|%{$_;}};"
cmd = 'powershell.exe'
result = {}
cnt = 0

def exp(line):
    try:
        script = redir + line.strip('\n') + '\n'
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(script.encode('utf-8'))
        res = out.split(b'\n')[6].strip().decode('gbk')
        
        if('while' in res or 'sleep' in res):
            return res
        if(res == '' or 'F:\\CNSS>' in res or '无法将' in res or '无效的' in res or '然后' in res or '不能' in res):
            raise Exception('error')
        return exp(res)
    except Exception as e:
        return line

def run(key, cnt):
    result[key] = []
    for x, line in enumerate(hash_dict[key].split(';')):
        print(cnt, x)
        result[key].append(exp(line))
    
t = []
for key in hash_dict.keys():
    t.append(Thread(target=run, args=(key,cnt,)))
    t[-1].start()
    cnt += 1
    if cnt % 10 == 0:
        for x in t:
            x.join()
        t = []

print(cnt)

with open('result.json', 'w') as f:
    f.write(dumps(result))
```

~好羡慕你们坚实的代码基础啊~

#### 逻辑分析

在反混淆后的对应代码中，大部分都是恶意代码，但是可以发现如下形式的代码：

```powershell
iex($M[@(103029045898495106128140488393279490731,283962955136589324103060025895380071615,100347917729209686340069745617547349730,238405316955808243927606563710399446649,218698919069890324731296928086576483285,13940646367990748425698245588557690704,233558059221060425999304675733838234320,129692624346663502335241542240082220070,35082001525670982399453018046361223701,328520292299326032765832843219896353365,22937617477989053507015679147587112829,83375175731001160297499272972594268643,181113447597478873176042023659491087625,133078815375884196401153883379379993112,222768486184364264889018742183865405471,180102119900859063039430119683397492538)[$tt.Dequeue()]]);
```

结合之前对输入的处理：

```powershell
[System.Collections.Queue]$tt=([byte[]][char[]]$t|%{$_ -shr 4;$_%16});
iex($M[129693309641433576095262078804193086780])
```

不难发现就是把flag每一位按照高四位和低四位拆开作为每次跳转的索引，恢复出每个`key`对应的跳转目标找到跳转路径即可。

可以发现93920216895015486878992607137045760151对应的代码是输出`Congratulations! you get the correct flag`字符串，程序的入口是`129693309641433576095262078804193086780`，反向寻找路径并组合。

```python
import json
with open("result.json", "r") as f:
	dic = json.load(f)

now = dict()

for key in dic:
	for x in dic[key]:
		if "$tt.Dequeue()" in x:
			now[key] = x[9:-19].split(",")

start = '93920216895015486878992607137045760151'
fin = '129693309641433576095262078804193086780'
flag = []
while start != fin:
	for key in now.keys():
		if start in now[key]:
			for i in range(len(now[key])):
				if now[key][i] == start:
					flag.append(i)
					break
			start = key
			break

print(flag)
i = len(flag)-1
while i >= 0:
	c = (flag[i] << 4) + flag[i-1]
	print(chr(c), end="")
	i -= 2
```

### 总结

虽然看起来是狗屎但是其实做起来还好（如果有思路的话），但是这平台是烂的我不好说。

