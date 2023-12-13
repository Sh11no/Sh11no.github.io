# 0ctf/tctf2023-0gn nodejs引擎魔改分析


## 碎碎念

本文也可以改名《Shino 为什么是一个啥比》，一个首波逆向题坐牢两天没做出来（还是我太菜了）

主要是复盘记录一下当时做题的几个思路和分析以及反思，虽然都没有成功但是也算一次经验积累，以供以后参考。

## 赛时分析



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


