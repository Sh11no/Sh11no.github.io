# 0ctf/tctf2023-0gn nodejs引擎魔改分析


## 碎碎念

本文也可以改名《Shino 为什么是一个啥比》，一个首波逆向题坐牢两天没做出来（还是我太菜了）

主要是复盘记录一下当时做题的几个思路和分析以及反思，虽然都没有成功但是也算一次经验积累，以供以后参考。

## 赛时分析

### js部分 解混淆

首先格式化一下js，然后简单看一下混淆的大概pattern。

有一个函数表，类似这样（节选）

```javascript
var i = {
		'kwUyT': '3|6|4|2|0|1|5',
		'ayHHB': function(H, I) {
			return H & I;
		},
		'gqHZW': function(H, I) {
			return H & I;
		},
		'bLOAn': function(H, I) {
			return H ^ I;
		},
		'NoEaD': function(H, I) {
			return H & I;
		},
		'ZUNMN': function(H, I) {
			return H ^ I;
		},
		'HpUmq': function(H, I) {
			return H ^ I;
		},
		'GXcYX': function(H, I) {
			return H ^ I;
		},
		'fMkag': function(H, I, J) {
			return H(I, J);
		},
		'WtIoQ': function(H, I, J) {
			return H(I, J);
		}
}
```

调用类似下面这个形式（节选）：

```javascript
function o(H, I, J, K, L, M, N) {
		H = i['fMkag'](j, H, i['WtIoQ'](j, i['WtIoQ'](j, i['NkvbM'](i['wJaTT'](I, J), i['wJaTT'](~I, K)), L), N));
		return i['TXoAD'](j, i['Hhvlr'](H << M, H >>> i['rJNAG'](0x20, M)), I);
	}
```

这里解混淆的思路是显然的，通过正则或手动将被混淆的函数名直接替换为对应的操作。如：

```javascript
'bLOAn': function(H, I) {
	return H ^ I;
}
```

搜索代码中全部的`'bLOAn'`替换为`^`，可以获得完整可读的代码逻辑。

这里通过常量识别可以发现是一个md5，没有任何魔改，哈希结果对应的即为默认输入`flag{00000000000000000000000000000000}`。但是输出结果为`Wrong!`，可以判断是nodejs被魔改。

> 这里由于我 md5 见得不多（由于哈希算法不可逆一般不会在逆向中出现）硬是看了半天，经队友@Mason 提醒才看出来是 md5 算法，最丢人的一集

### nodejs 魔改点初步定位

尝试进行黑盒测试来猜测 nodejs 的魔改位置。我们先看一下整体 js 进行 flagcheck 的流程：

```javascript
class a {
	static['resultchecker'](c) {
		var d = {
			'vZhID': function(f, g) {
				return f(g);
			},
			'EVeqn': function(f, g) {
				return f == g;
			},
			'TgcSD': 'cd9e459ea708a948d5c2f5a6ca8838cf'
		};
		var e = d['vZhID'](MMM, c); //md5
		if (d['EVeqn'](e, d['TgcSD'])) {
			return 0x0; //pos1
		} else {
			return -0x1;
		}
	}
	static['flagchecker']() {
		if (c['=='](process['argv']['length'], 0x3)) {
			var d = process['argv'][0x2];
			console['log'](c['your_input_is'], d);
		} else {
			return -0x1;
		}
		if (c['!='](d['length'], 0x26)) {
			return -0x1;
		}
		//flag 格式 check 省略
		var e = d['slice'](0x5, c['+'](0x5, 0x20));
		e = new Buffer['from'](e);
		if (a['resultchecker'](e) != 0x0) {
			return -0x1; //pos2
		}
		return 0x0;
	}
}
function b() {
	if (a['flagchecker']() == 0x0) {
		console['log']('Right!');
	} else {
		console['log']('Wrong!'); //pos3
	}
}
b();
```

这里我们先假设 nodejs 没有对被运行的 js 进行完整性校验，即我们可以用他的引擎运行任意的脚本进行测试。如果测试中可以触发`Right!`则可以判定不存在这种可能。

通过在脚本中进行`console.log`，可以发现输入 flag 为 `flag{00000000000000000000000000000000}` 时，得到的执行路径是 pos1->pos2->pos3 （在上面代码中标出）

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

下载nodejsv16.18.0找到源码：src/interpreter/bytecode-generator.cc

在 switch case 的 2 3 8，对应源码的三种调用方法：

```c++
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

```c++
v33 = v8::internal::interpreter::BytecodeRegisterAllocator::NewRegister(v916);
v8::internal::interpreter::BytecodeArrayBuilder::LoadLiteral(v26, 0LL);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v33);
v36 = v8::internal::FeedbackVectorSpec::AddSlot(*(_QWORD *)(a1 + 504) + 56LL, 8LL, v34, v35);
v8::internal::interpreter::BytecodeArrayBuilder::LoadKeyedProperty(v26, v32, v36);
v39 = v8::internal::FeedbackVectorSpec::AddSlot(*(_QWORD *)(a1 + 504) + 56LL, 15LL, v37, v38);
v8::internal::interpreter::BytecodeArrayBuilder::BinaryOperationSmiLiteral(
    (__int64)v26,
    38,
    0x3E00000000LL,
    v39);
v42 = *(_QWORD *)(a1 + 528);
v43 = *(_BYTE *)(v42 + 121) & 1;
if ( (*(_BYTE *)(v42 + 121) & 1) != 0 )
{
    v44 = *(_QWORD *)(a1 + 504);
    v45 = 13LL;
}
else
{
    v44 = *(_QWORD *)(a1 + 504);
    v45 = 3LL;
}
```

比较关键的是这个：`v8::internal::interpreter::BytecodeArrayBuilder::BinaryOperationSmiLiteral(v26,38,0x3E00000000LL,v39);`

源码：src/interpreter/bytecode-array-builder.h

运算token定义：src/parsing/token.h

操作有38、47、48三种，分别对应：

- 38：BIT_XOR
- 47：ADD
- 48：SUB

算法流程为修改输入之后调用以下逻辑，以下逻辑执行完毕后修改回去。

```c++
v449 = v8::internal::FeedbackVectorSpec::AddSlot(v447 + 56, v448, v443, v444);
v8::internal::interpreter::BytecodeArrayBuilder::StoreKeyedProperty(v26, v32, v33, v449, v446);
v8::internal::interpreter::BytecodeArrayBuilder::LoadLiteral(v26, 0x6A8838CF00000000LL);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v921);
v8::internal::interpreter::BytecodeArrayBuilder::CallRuntime(v26, 475LL, params_count);
v922 = v8::internal::interpreter::BytecodeRegisterAllocator::NewRegister(v916);
v8::internal::interpreter::BytecodeArrayBuilder::StoreAccumulatorInRegister(v26, v922);
```

调用了 475 号 Runtime 函数，参考https://zhuanlan.zhihu.com/p/431621841

```c++
char *__fastcall v8::internal::Runtime::FunctionForId(int a1)
{
  return (char *)&unk_555E3A49FD00 + 32 * a1; 
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
	x = (x+0x100-i)&0xFF
	if op[i] == 38:
		return chr((x^data[i])&0xff)
	if op[i] == 47:
		return chr((x+0x100-data[i])&0xff)
	if op[i] == 48:
		return chr((x+data[i])&0xff)
def long_to_arr(x):
	return [x&0xff, (x>>8)&0xff, (x>>16)&0xff, (x>>24)&0xff]
def arr_to_long(x):
	return x[0]+(x[1]<<8)+(x[2]<<16)+(x[3]<<24)

def tea(v46, v47, v44_LO, v44_HI):
	v42 = 0x5e9a8211
	v43 = 0x1c108262	
	v45 = 0xF4DCA6E0
	while v45 != 0:
		v47 += 0x100000000
		v47 -= ((v45 + v46)&0xFFFFFFFF) ^ ((v43 + ((v46 >> 5)&0xFFFFFFFF))&0xFFFFFFFF) ^ ((v42 + ((v46 << 4)&0xFFFFFFFF))&0xFFFFFFFF)
		v47 &= 0xFFFFFFFF

		v46 += 0x100000000
		v46 -= ((v47 + v45)&0xFFFFFFFF) ^ ((v43 + ((v47 >> 5)&0xFFFFFFFF))&0xFFFFFFFF) ^ ((v42 + ((v47 << 4)&0xFFFFFFFF))&0xFFFFFFFF)
		v46 &= 0xFFFFFFFF

		v45 += 0x68591AC9
		v45 &= 0xFFFFFFFF
	v46 ^= v44_LO
	v47 ^= v44_HI
	return v46, v47

v40 = 0x6a8838cf
v44_HI = v40 ^ 0xA14BC8DF
v44_LO = v40 ^ 0x6527B8CF

for i in range(0, 32, 8):
	a, b = tea(arr_to_long(cip[i:i+4]), arr_to_long(cip[i+4:i+8]), v44_LO, v44_HI)
	v44_LO = arr_to_long(cip[i:i+4])
	v44_HI = arr_to_long(cip[i+4:i+8])
	arr = long_to_arr(a) + long_to_arr(b)
	for j in range(8):
		print(convert(arr[j], i+j), end="")
```

`flag{97170f6727bc6757e69eb04c045478be}`

