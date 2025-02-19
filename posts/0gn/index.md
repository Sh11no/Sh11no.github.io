# 0ctf/Tctf2023-0gn Nodejs引擎魔改分析


## 碎碎念

本文也可以改名《Shino 为什么是一个啥比》，一个首波逆向题坐牢两天没做出来（还是我太菜了）

主要是复盘记录一下当时做题的几个思路和分析以及反思，虽然都没有成功但是也算一次经验积累，以供以后参考。

## 赛时分析

### js部分 解混淆

首先格式化一下js，然后简单看一下混淆的大概pattern。

有一个函数表，类似这样（节选）

```javascript
var i = {
		&#39;kwUyT&#39;: &#39;3|6|4|2|0|1|5&#39;,
		&#39;ayHHB&#39;: function(H, I) {
			return H &amp; I;
		},
		&#39;gqHZW&#39;: function(H, I) {
			return H &amp; I;
		},
		&#39;bLOAn&#39;: function(H, I) {
			return H ^ I;
		},
		&#39;NoEaD&#39;: function(H, I) {
			return H &amp; I;
		},
		&#39;ZUNMN&#39;: function(H, I) {
			return H ^ I;
		},
		&#39;HpUmq&#39;: function(H, I) {
			return H ^ I;
		},
		&#39;GXcYX&#39;: function(H, I) {
			return H ^ I;
		},
		&#39;fMkag&#39;: function(H, I, J) {
			return H(I, J);
		},
		&#39;WtIoQ&#39;: function(H, I, J) {
			return H(I, J);
		}
}
```

这里解混淆的思路是显然的，通过正则或手动将被混淆的函数名直接替换为对应的操作。如：

```javascript
&#39;bLOAn&#39;: function(H, I) {
	return H ^ I;
}
```

搜索代码中全部的`&#39;bLOAn&#39;`替换为`^`，可以获得完整可读的代码逻辑。

这里通过常量识别可以发现是一个md5，没有任何魔改，哈希结果对应的即为默认输入`flag{00000000000000000000000000000000}`。但是输出结果为`Wrong!`，可以判断是nodejs被魔改。

### nodejs 魔改点初步定位

尝试进行黑盒测试来猜测 nodejs 的魔改位置。我们先看一下整体 js 进行 flagcheck 的流程：

```javascript
class a {
	static[&#39;resultchecker&#39;](c) {
		var d = {
			&#39;vZhID&#39;: function(f, g) {
				return f(g);
			},
			&#39;EVeqn&#39;: function(f, g) {
				return f == g;
			},
			&#39;TgcSD&#39;: &#39;cd9e459ea708a948d5c2f5a6ca8838cf&#39;
		};
		var e = d[&#39;vZhID&#39;](MMM, c); //md5
		if (d[&#39;EVeqn&#39;](e, d[&#39;TgcSD&#39;])) {
			return 0x0; //pos1
		} else {
			return -0x1;
		}
	}
	static[&#39;flagchecker&#39;]() {
		if (c[&#39;==&#39;](process[&#39;argv&#39;][&#39;length&#39;], 0x3)) {
			var d = process[&#39;argv&#39;][0x2];
			console[&#39;log&#39;](c[&#39;your_input_is&#39;], d);
		} else {
			return -0x1;
		}
		if (c[&#39;!=&#39;](d[&#39;length&#39;], 0x26)) {
			return -0x1;
		}
		//flag 格式 check 省略
		var e = d[&#39;slice&#39;](0x5, c[&#39;&#43;&#39;](0x5, 0x20));
		e = new Buffer[&#39;from&#39;](e);
		if (a[&#39;resultchecker&#39;](e) != 0x0) {
			return -0x1; //pos2
		}
		return 0x0;
	}
}
function b() {
	if (a[&#39;flagchecker&#39;]() == 0x0) {
		console[&#39;log&#39;](&#39;Right!&#39;);
	} else {
		console[&#39;log&#39;](&#39;Wrong!&#39;); //pos3
	}
}
b();
```

这里我们先假设 nodejs 没有对被运行的 js 进行完整性校验，即我们可以用他的引擎运行任意的脚本进行测试。如果测试中可以触发`Right!`则可以判定不存在这种可能。

通过在脚本中进行`console.log`，可以发现输入 flag 为 `flag{00000000000000000000000000000000}` 时，得到的执行路径是 pos1-&gt;pos2-&gt;pos3 （在上面代码中标出）

这里可以发现`resultchecker`的执行到`return 0x0`，但是主函数得到的返回值却是`-0x1`矛盾。

我们来思考一下几种可能性并且用我们观察到的现象来验证一下：

- `resultchecker`中的某些运算符被重载或常量被替换：
  - 尝试在 pos1 处输出 e 和密文，发现他们没被更改，且`==`正常工作（返回true），否定这种可能性
- `resultchecker`被替换：
  - 在 pos1 处添加的输出语句能被执行，说明`resultchecker`内的逻辑有被执行，否定这种可能性
- `resultchecker`被某种方式 hook （可能的）
- `Return`或其相关的字节码解析操作被改写（可能的）

注意到上面的3、4操作本质上是相同的。

### hook 时机和条件定位

一般来说 hook 一个函数必须要先找到这个函数。虽然我不会 js，但是这些方法一般是通用的。寻找函数的方法大概如下（可能我经验不足接触得较少）：

- 函数名称
- 函数签名
- 函数偏移
- 函数特征（一般是特征字符串的引用）

简单进行一下测试：

```javascript
class a {
    static resultchecker(c) {
        return 0; //result: -1
    }
    static resultche2ker(c) {
        return 0; //result: 0
    }
    static aaaresultcheckeraaa(c) {
        return 0; //result: -1
    }
    static resultchecker(c, c) { //实际上这里是分两次测试的，为了好看写在一起，下同
        return 0; //result: 0
    }
    static resultchecker(c) {
        return 114514; //result: 114514
    }
}
class b {
    static resultchecker(c) {
        return 0; //result: -1
    }
}
```

可以得出函数触发 hook 的条件为：

- 函数名中包含`resultchecker`字符串
- 返回0或-1（这里-1无法被验证）
- 只传入一个参数

这里很明显是通过函数名称来定位的函数，同时因为 hook 是否触发与返回值有关，因此 hook 时机一定在 return  之后。

### hook 函数定位

由于没有发现可见字符串`resultchecker`（详见“复盘”节《为什么说 Shino 是一个啥比》），尝试通过以下方法进行  hook 函数定位。这里就是记录一下，实际上没有能跑通的方法。

由于我对 nodejs 内核没有任何的了解，所以我的调试方法是添加`console.log`语句并且监控`write`系统调用（只要有输出必定有调用）来在 js 函数内部添加断点。

由于我的 Cheat Engine 爆炸了，并且没有合适的时机进行 Attach （这里我觉得是我技不如人），所以没有先把程序跑起来再在内存中搜可见字符串这种操作（这里我觉得是我技不如人，我觉得这个方法应该是可行的，等师傅们教我）

- 调用链 diff （忘了hook时机在 return 之后，弱智了）
- Bindiff
  - 实际上由于题目的 nodejs 的编译环境和官方的完全不一样，导入的模块也不一样，可以说结果没有一点相同的
- 跟踪输入下读写断点
  - 在 String 的 New 方法里找输入（没找到）
  - 在 Argument Parse 的相关方法里找输入（没找到）
  - 或者说我连上面那两个方法都没找到，好吧（其实我的ida完全不能完整加载这个node的binary（太大了），所以我没法进行函数搜索或者等等操作，一搜索就会卡死，该换电脑了）
- 跟踪字节码编译或 log 执行的字节码
  - 这种情况仅限于 hook 代码也在 js 层，事实上 hook 代码是在引擎里的，所以这里的相关尝试都失败了
- 针对字节码魔改：
  - diff 字节码表，使用 nodejs 自带的 log 来记录字节码记录顺序

在最后一步的尝试中我们确实知道了是在 Bytecode 的相关方法内进行了魔改，但是直到比赛结束也没有找到这个方法。

## 复盘

### 为什么说 Shino 是一个啥比

接下来揭秘一下我为什么没有找到可见字符串。

![](/images/0gn-1.png)

划重点：这种短字符串常量会被编译优化为上面这个样子，所以如果在 hex 里搜索`resultch`（8位）是可以搜到的，但是`resultchecker`不行。

菜死我了，长记性了（但凡打字慢一点就搜到了，我也搜过hex

### hook 逻辑分析

修改点位于`v8::internal::interpreter::BytecodeGenerator::VisitCall`

下载nodejsv16.18.0找到源码：`src/interpreter/bytecode-generator.cc`

在 switch case 的 2 3 8，对应源码的三种调用方法：

```c&#43;&#43;
case Call::NAMED_PROPERTY_CALL:
case Call::KEYED_PROPERTY_CALL:
case Call::PRIVATE_CALL:
```

判断函数名称中包含`resultchecker`:

![](/images/0gn-2.png)

并且参数个数为2（还有一个`this.context`）：

![](/images/0gn-3.png)

满足以上条件的时候执行一些额外操作。

看起来操作是按位比较，每一位比较的逻辑大致如下：

```c&#43;&#43;
v33 = v8::internal::interpreter::BytecodeRegisterAllocator::NewRegister(v916);
v8::internal::interpreter::BytecodeArrayBuilder::LoadLiteral(v26, 0LL);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v33);
v36 = v8::internal::FeedbackVectorSpec::AddSlot(*(_QWORD *)(a1 &#43; 504) &#43; 56LL, 8LL, v34, v35);
v8::internal::interpreter::BytecodeArrayBuilder::LoadKeyedProperty(v26, v32, v36);
v39 = v8::internal::FeedbackVectorSpec::AddSlot(*(_QWORD *)(a1 &#43; 504) &#43; 56LL, 15LL, v37, v38);
v8::internal::interpreter::BytecodeArrayBuilder::BinaryOperationSmiLiteral(
    (__int64)v26,
    38,
    0x3E00000000LL,
    v39);
v42 = *(_QWORD *)(a1 &#43; 528);
v43 = *(_BYTE *)(v42 &#43; 121) &amp; 1;
if ( (*(_BYTE *)(v42 &#43; 121) &amp; 1) != 0 )
{
    v44 = *(_QWORD *)(a1 &#43; 504);
    v45 = 13LL;
}
else
{
    v44 = *(_QWORD *)(a1 &#43; 504);
    v45 = 3LL;
}
```

比较关键的是这个：`v8::internal::interpreter::BytecodeArrayBuilder::BinaryOperationSmiLiteral(v26,38,0x3E00000000LL,v39);`

源码：`src/interpreter/bytecode-array-builder.h`

运算token定义：`src/parsing/token.h`

操作有38、47、48三种，分别对应：

- 38：BIT_XOR
- 47：ADD
- 48：SUB

算法流程为修改输入之后调用以下逻辑，以下逻辑执行完毕后修改回去。

```c&#43;&#43;
v449 = v8::internal::FeedbackVectorSpec::AddSlot(v447 &#43; 56, v448, v443, v444);
v8::internal::interpreter::BytecodeArrayBuilder::StoreKeyedProperty(v26, v32, v33, v449, v446);
v8::internal::interpreter::BytecodeArrayBuilder::LoadLiteral(v26, 0x6A8838CF00000000LL);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v921);
v8::internal::interpreter::BytecodeArrayBuilder::CallRuntime(v26, 475LL, params_count);
v922 = v8::internal::interpreter::BytecodeRegisterAllocator::NewRegister(v916);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v922);
```

调用了 475 号 Runtime 函数，参考https://zhuanlan.zhihu.com/p/431621841

```c&#43;&#43;
char *__fastcall v8::internal::Runtime::FunctionForId(int a1)
{
  return (char *)&amp;unk_555E3A49FD00 &#43; 32 * a1; 
}
```

通过上面的函数表可知调用了函数 v8::internal::Runtime_TypedArrayVerify，可以看到这个函数被改动过，包含一个check逻辑

![](/images/0gn-4.png)

逆向算法即可得到答案。

exp（有点难调）

```python
cip = [0x28, 0xA5, 0xA9, 0xCD, 0x34, 0x0A, 0xB9, 0xB2, 0xF2, 0x54, 
  0xE5, 0x56, 0x68, 0x41, 0xFD, 0xEE, 0x1A, 0xE8, 0x33, 0xB3, 
  0x25, 0x8A, 0x97, 0xB9, 0xD0, 0xAC, 0xCD, 0xF0, 0x85, 0xBA, 
  0x07, 0xEB]
op = [38, 47, 47, 47, 47, 48, 48, 47, 48, 48, 48, 48, 48, 38, 47, 48, 47, 38, 48, 47, 38, 47, 38, 48, 47, 48, 38, 47, 38, 38, 47, 48]
data = [0x3e, 0x64, 0x5c, 0x22, 0xe7, 0x7a, 0x17, 0xa2, 0xa2, 0xd2, 0xef, 0xb9, 0x76, 0x63, 0x11, 0x1c, 0xe2, 0x0b, 0x48, 0x2d, 0x87, 0xb7, 0x46, 0x07, 0xf2, 0x1a, 0xc4, 0x81, 0x3a, 0x87, 0x76, 0x6e]

def convert(x, i):
	x = (x&#43;0x100-i)&amp;0xFF
	if op[i] == 38:
		return chr((x^data[i])&amp;0xff)
	if op[i] == 47:
		return chr((x&#43;0x100-data[i])&amp;0xff)
	if op[i] == 48:
		return chr((x&#43;data[i])&amp;0xff)
def long_to_arr(x):
	return [x&amp;0xff, (x&gt;&gt;8)&amp;0xff, (x&gt;&gt;16)&amp;0xff, (x&gt;&gt;24)&amp;0xff]
def arr_to_long(x):
	return x[0]&#43;(x[1]&lt;&lt;8)&#43;(x[2]&lt;&lt;16)&#43;(x[3]&lt;&lt;24)

def tea(v46, v47, v44_LO, v44_HI):
	v42 = 0x5e9a8211
	v43 = 0x1c108262	
	v45 = 0xF4DCA6E0
	while v45 != 0:
		v47 &#43;= 0x100000000
		v47 -= ((v45 &#43; v46)&amp;0xFFFFFFFF) ^ ((v43 &#43; ((v46 &gt;&gt; 5)&amp;0xFFFFFFFF))&amp;0xFFFFFFFF) ^ ((v42 &#43; ((v46 &lt;&lt; 4)&amp;0xFFFFFFFF))&amp;0xFFFFFFFF)
		v47 &amp;= 0xFFFFFFFF

		v46 &#43;= 0x100000000
		v46 -= ((v47 &#43; v45)&amp;0xFFFFFFFF) ^ ((v43 &#43; ((v47 &gt;&gt; 5)&amp;0xFFFFFFFF))&amp;0xFFFFFFFF) ^ ((v42 &#43; ((v47 &lt;&lt; 4)&amp;0xFFFFFFFF))&amp;0xFFFFFFFF)
		v46 &amp;= 0xFFFFFFFF

		v45 &#43;= 0x68591AC9
		v45 &amp;= 0xFFFFFFFF
	v46 ^= v44_LO
	v47 ^= v44_HI
	return v46, v47

v40 = 0x6a8838cf
v44_HI = v40 ^ 0xA14BC8DF
v44_LO = v40 ^ 0x6527B8CF

for i in range(0, 32, 8):
	a, b = tea(arr_to_long(cip[i:i&#43;4]), arr_to_long(cip[i&#43;4:i&#43;8]), v44_LO, v44_HI)
	v44_LO = arr_to_long(cip[i:i&#43;4])
	v44_HI = arr_to_long(cip[i&#43;4:i&#43;8])
	arr = long_to_arr(a) &#43; long_to_arr(b)
	for j in range(8):
		print(convert(arr[j], i&#43;j), end=&#34;&#34;)
```

`flag{97170f6727bc6757e69eb04c045478be}`


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/0gn/  

