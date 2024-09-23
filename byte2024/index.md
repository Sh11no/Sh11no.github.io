# ByteCTF2024 Reverse wps


## 碎碎念

好久没打 CTF 感觉能力退化了不少，遇到不是 Android 的题都有点不会做了，甚至卡了一题光荣成为战犯(?)。想了半天为什么 10 解的题我都不会做，后来发现原来现在还有可以直接去除的 ollvm 混淆.... 平时看到的 ollvm 混淆基本都是加强过的根本没法直接跑轮子去除就根本没往这方面想，还是有点太唐了。

## babyAPK

上来肯定是先把 Android 秒了(x

经典 flutter，直接跑一下 blutter。 main.dart 里可以看到一个明显的相关逻辑：

```
_ test(/* No info */) {
    // ** addr: 0x264c0c, size: 0x17c
    // 0x264c0c: EnterFrame
    //     0x264c0c: stp             fp, lr, [SP, #-0x10]!
    //     0x264c10: mov             fp, SP
    // 0x264c14: AllocStack(0x28)
    //     0x264c14: sub             SP, SP, #0x28
    // 0x264c18: CheckStackOverflow
    //     0x264c18: ldr             x16, [THR, #0x38]  ; THR::stack_limit
    //     0x264c1c: cmp             SP, x16
    //     0x264c20: b.ls            #0x264d78
    // 0x264c24: LoadField: r0 = r1->field_13
    //     0x264c24: ldur            w0, [x1, #0x13]
    // 0x264c28: DecompressPointer r0
    //     0x264c28: add             x0, x0, HEAP, lsl #32
    // 0x264c2c: LoadField: r1 = r0->field_27
    //     0x264c2c: ldur            w1, [x0, #0x27]
    // 0x264c30: DecompressPointer r1
    //     0x264c30: add             x1, x1, HEAP, lsl #32
    // 0x264c34: LoadField: r0 = r1->field_7
    //     0x264c34: ldur            w0, [x1, #7]
    // 0x264c38: DecompressPointer r0
    //     0x264c38: add             x0, x0, HEAP, lsl #32
    // 0x264c3c: mov             x1, x0
    // 0x264c40: stur            x0, [fp, #-8]
    // 0x264c44: r2 = "ByteCTF{"
    //     0x264c44: add             x2, PP, #0xc, lsl #12  ; [pp+0xcfb0] "ByteCTF{"
    //     0x264c48: ldr             x2, [x2, #0xfb0]
    // 0x264c4c: r4 = const [0, 0x2, 0, 0x2, null]
    //     0x264c4c: ldr             x4, [PP, #0x170]  ; [pp+0x170] List(5) [0, 0x2, 0, 0x2, Null]
    // 0x264c50: r0 = startsWith()
    //     0x264c50: bl              #0x198d18  ; [dart:core] _StringBase::startsWith
    // 0x264c54: tbnz            w0, #4, #0x264d58
    // 0x264c58: ldur            x1, [fp, #-8]
    // 0x264c5c: LoadField: r0 = r1->field_7
    //     0x264c5c: ldur            w0, [x1, #7]
    // 0x264c60: r2 = LoadInt32Instr(r0)
    //     0x264c60: sbfx            x2, x0, #1, #0x1f
    // 0x264c64: stur            x2, [fp, #-0x10]
    // 0x264c68: sub             x0, x2, #1
    // 0x264c6c: lsl             x3, x0, #1
    // 0x264c70: stp             x3, x1, [SP, #8]
    // 0x264c74: r16 = "}"
    //     0x264c74: add             x16, PP, #8, lsl #12  ; [pp+0x8a40] "}"
    //     0x264c78: ldr             x16, [x16, #0xa40]
    // 0x264c7c: str             x16, [SP]
    // 0x264c80: r0 = _substringMatches()
    //     0x264c80: bl              #0x198df8  ; [dart:core] _StringBase::_substringMatches
    // 0x264c84: tbnz            w0, #4, #0x264d58
    // 0x264c88: ldur            x0, [fp, #-0x10]
    // 0x264c8c: cmp             x0, #0x2d
    // 0x264c90: b.ne            #0x264d58
    // 0x264c94: ldur            x1, [fp, #-8]
    // 0x264c98: r0 = LoadClassIdInstr(r1)
    //     0x264c98: ldur            x0, [x1, #-1]
    //     0x264c9c: ubfx            x0, x0, #0xc, #0x14
    // 0x264ca0: r2 = "{"
    //     0x264ca0: add             x2, PP, #8, lsl #12  ; [pp+0x8a18] "{"
    //     0x264ca4: ldr             x2, [x2, #0xa18]
    // 0x264ca8: r0 = GDT[cid_x0 + -0x1000]()
    //     0x264ca8: sub             lr, x0, #1, lsl #12
    //     0x264cac: ldr             lr, [x21, lr, lsl #3]
    //     0x264cb0: blr             lr
    // 0x264cb4: mov             x2, x0
    // 0x264cb8: LoadField: r0 = r2->field_b
    //     0x264cb8: ldur            w0, [x2, #0xb]
    // 0x264cbc: r1 = LoadInt32Instr(r0)
    //     0x264cbc: sbfx            x1, x0, #1, #0x1f
    // 0x264cc0: mov             x0, x1
    // 0x264cc4: r1 = 1
    //     0x264cc4: movz            x1, #0x1
    // 0x264cc8: cmp             x1, x0
    // 0x264ccc: b.hs            #0x264d80
    // 0x264cd0: LoadField: r0 = r2->field_f
    //     0x264cd0: ldur            w0, [x2, #0xf]
    // 0x264cd4: DecompressPointer r0
    //     0x264cd4: add             x0, x0, HEAP, lsl #32
    // 0x264cd8: LoadField: r1 = r0->field_13
    //     0x264cd8: ldur            w1, [x0, #0x13]
    // 0x264cdc: DecompressPointer r1
    //     0x264cdc: add             x1, x1, HEAP, lsl #32
    // 0x264ce0: r0 = LoadClassIdInstr(r1)
    //     0x264ce0: ldur            x0, [x1, #-1]
    //     0x264ce4: ubfx            x0, x0, #0xc, #0x14
    // 0x264ce8: r2 = "}"
    //     0x264ce8: add             x2, PP, #8, lsl #12  ; [pp+0x8a40] "}"
    //     0x264cec: ldr             x2, [x2, #0xa40]
    // 0x264cf0: r0 = GDT[cid_x0 + -0x1000]()
    //     0x264cf0: sub             lr, x0, #1, lsl #12
    //     0x264cf4: ldr             lr, [x21, lr, lsl #3]
    //     0x264cf8: blr             lr
    // 0x264cfc: mov             x2, x0
    // 0x264d00: LoadField: r0 = r2->field_b
    //     0x264d00: ldur            w0, [x2, #0xb]
    // 0x264d04: r1 = LoadInt32Instr(r0)
    //     0x264d04: sbfx            x1, x0, #1, #0x1f
    // 0x264d08: mov             x0, x1
    // 0x264d0c: r1 = 0
    //     0x264d0c: movz            x1, #0
    // 0x264d10: cmp             x1, x0
    // 0x264d14: b.hs            #0x264d84
    // 0x264d18: LoadField: r0 = r2->field_f
    //     0x264d18: ldur            w0, [x2, #0xf]
    // 0x264d1c: DecompressPointer r0
    //     0x264d1c: add             x0, x0, HEAP, lsl #32
    // 0x264d20: LoadField: r1 = r0->field_f
    //     0x264d20: ldur            w1, [x0, #0xf]
    // 0x264d24: DecompressPointer r1
    //     0x264d24: add             x1, x1, HEAP, lsl #32
    // 0x264d28: r0 = m3N4B5V6()
    //     0x264d28: bl              #0x265088  ; [package:babyapk/src/rust/api/simple.dart] ::m3N4B5V6
    // 0x264d2c: tbnz            w0, #4, #0x264d44
    // 0x264d30: r1 = "You Got it!!!!"
    //     0x264d30: add             x1, PP, #0xc, lsl #12  ; [pp+0xcfb8] "You Got it!!!!"
    //     0x264d34: ldr             x1, [x1, #0xfb8]
    // 0x264d38: r4 = const [0, 0x1, 0, 0x1, null]
    //     0x264d38: ldr             x4, [PP, #0x430]  ; [pp+0x430] List(5) [0, 0x1, 0, 0x1, Null]
    // 0x264d3c: r0 = showToast()
    //     0x264d3c: bl              #0x264d88  ; [package:fluttertoast/fluttertoast.dart] Fluttertoast::showToast
    // 0x264d40: b               #0x264d68
    // 0x264d44: r1 = "wrong flag"
    //     0x264d44: add             x1, PP, #0xc, lsl #12  ; [pp+0xcfc0] "wrong flag"
    //     0x264d48: ldr             x1, [x1, #0xfc0]
    // 0x264d4c: r4 = const [0, 0x1, 0, 0x1, null]
    //     0x264d4c: ldr             x4, [PP, #0x430]  ; [pp+0x430] List(5) [0, 0x1, 0, 0x1, Null]
    // 0x264d50: r0 = showToast()
    //     0x264d50: bl              #0x264d88  ; [package:fluttertoast/fluttertoast.dart] Fluttertoast::showToast
    // 0x264d54: b               #0x264d68
    // 0x264d58: r1 = "wrong flag"
    //     0x264d58: add             x1, PP, #0xc, lsl #12  ; [pp+0xcfc0] "wrong flag"
    //     0x264d5c: ldr             x1, [x1, #0xfc0]
    // 0x264d60: r4 = const [0, 0x1, 0, 0x1, null]
    //     0x264d60: ldr             x4, [PP, #0x430]  ; [pp+0x430] List(5) [0, 0x1, 0, 0x1, Null]
    // 0x264d64: r0 = showToast()
    //     0x264d64: bl              #0x264d88  ; [package:fluttertoast/fluttertoast.dart] Fluttertoast::showToast
    // 0x264d68: r0 = Null
    //     0x264d68: mov             x0, NULL
    // 0x264d6c: LeaveFrame
    //     0x264d6c: mov             SP, fp
    //     0x264d70: ldp             fp, lr, [SP], #0x10
    // 0x264d74: ret
    //     0x264d74: ret             
    // 0x264d78: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x264d78: bl              #0x3bbe84  ; StackOverflowSharedWithoutFPURegsStub
    // 0x264d7c: b               #0x264c24
    // 0x264d80: r0 = RangeErrorSharedWithoutFPURegs()
    //     0x264d80: bl              #0x3bc2cc  ; RangeErrorSharedWithoutFPURegsStub
    // 0x264d84: r0 = RangeErrorSharedWithoutFPURegs()
    //     0x264d84: bl              #0x3bc2cc  ; RangeErrorSharedWithoutFPURegsStub
  }
}
```

大概就是 check 了一下 flag 格式和长度 45，直接进入`[package:babyapk/src/rust/api/simple.dart] ::m3N4B5V6`执行校验逻辑。这里可以看到是使用了一个 flutter 和 rust 结合的框架 https://github.com/fzyzcjy/flutter_rust_bridge

 直接找源码来看，大概的逻辑是对所有的 rust 函数做一个中间层，大概的调用顺序如下：

```
package:babyapk/src/rust/api/simple.dart::m3N4B5V6
package:babyapk/src/rust/frb_generated.dart::crateApiSimpleM3N4B5V6
```

示例工程里的调用代码：https://github.com/fzyzcjy/flutter_rust_bridge/blob/fffbb1f9ab7e4586ec2e3cd7f1f0b94219161ee1/frb_example/dart_minimal/lib/src/rust/frb_generated.dart#L96

```dart
  @override
  Future<void> crateApiMinimalInitApp() {
    return handler.executeNormal(NormalTask(
      callFfi: (port_) {
        final serializer = SseSerializer(generalizedFrbRustBinding);
        pdeCallFfi(generalizedFrbRustBinding, serializer,
            funcId: 1, port: port_);
      },
      codec: SseCodec(
        decodeSuccessData: sse_decode_unit,
        decodeErrorData: null,
      ),
      constMeta: kCrateApiMinimalInitAppConstMeta,
      argValues: [],
      apiImpl: this,
    ));
  }
```

可以看到是调用 pdeCallFfi 后根据函数 ID 来调用函数。根据官方文档，序列化的一些东西只给 rust 访问 dart 对象的能力，所以可以不管他。

在 ida 里经过一系列 F7 分析后可以发现跳过一些异步的操作后直接走到了 CallNativeThroughSafepointStub_1815ac 来进行一个统一的调用，最后跳入 `librust_lib_babyapk.so+0x350b8` 再根据函数ID执行具体的函数逻辑。

出题人在这个 so 里留了一个 `m3N4B5V6` 的字符串，感觉之前的努力全部都像小丑，还好我起床的时候血都没了不然肯定要红温...

后面的逻辑是先 check 了 uuid 格式，然后 8 个一组解方程，感觉这 rust 和没有也一样。

```python
from z3 import *
x = [Int(f'x{i}') for i in range(8)]
c = [0x45158, -0x109A, 0x1D3F, 0x4C46B, -0x686, 0x1BFD, -0x45DCB, 0x1ED2]
s = Solver()
for i in range(8):
    s.add(x[i] > 0)
    s.add(x[i] < 128)

s.add(x[7] + x[1] * x[3] * x[5] - (x[0] + x[6] + x[2] * x[4]) == c[0])
s.add(x[3] - x[4] - x[0] * x[5] + x[7] * x[1] + x[2] + x[6] == c[1])
s.add(x[0] * x[5] - (x[4] + x[7] * x[1]) + x[2] + x[6] * x[3] == c[2])
s.add(x[1] + x[4] * x[0] - (x[7] + x[2]) + x[6] * x[5] * x[3] == c[3])
s.add(x[5] * x[3] + x[1] + x[2] * x[4] - (x[6] + x[7] * x[0]) == c[4])
s.add(x[0] * x[5] + x[1] * x[3] + x[2] - (x[6] + x[4] * x[7]) == c[5])
s.add(x[7] - x[1] + x[2] * x[5] + x[6] - x[4] * x[0] * x[3] == c[6])
s.add(x[3] - x[7] - (x[1] + x[5]) + x[4] * x[0] + x[6] * x[2] == c[7])

print(s.check())
m = s.model()
for i in range(8):
    print(chr(m[x[i]].as_long()), end="")
```

## ByteBuffer

不知道什么是 flatbuffer，但是一看有边有点多半就是画图，那么需要的信息就是边连接的两个点和点的坐标。直接大眼观察一下哪个像就可以了。大概内存布局：

```
Edge(3b0h)
0x10000000: pivot
0x77: 左端点编号
0x75: 右端点编号
0x4: 不知道
0x9: 名字长度
string: Edge #103(8byte对齐）
0xfffff1cc: 不知道

Dot(1234h)
0x640: x坐标
0x4b: y坐标
0x4: 不知道
0x8: 名字长度
string: Dot #120(8byte对齐)
0xfffff2c8: 不知道
```

直接画图。

```python
EDGE_START = 0x3b0
EDGE_END = 0x1234
DOT_START = 0x1234
DOT_END = 0x1fb0
EDGE_SIZE = 0x24
DOT_SIZE = 0x20
DOT_CNT = 120
EDGE_CNT = 103

with open("ByteBuffer.bin", "rb") as f:
	c = f.read()

dots = [None for i in range(DOT_CNT+1)]
index = DOT_CNT
i = DOT_START
while i < DOT_END:
	x = int.from_bytes(c[i:i+4], 'little')
	y = int.from_bytes(c[i+4:i+8], 'little')
	dots[index] = (x, y)
	index -= 1
	i += 16
	while int.from_bytes(c[i:i+4], 'little') != 4 and i < DOT_END:
		i += 1
	i -= 8
print(dots)
edges = []
i = EDGE_START
while i < EDGE_END:
	print(c[i+4:i+12])
	x = int.from_bytes(c[i+4:i+8], 'little')
	y = int.from_bytes(c[i+8:i+12], 'little')
	edges.append((x, y))
	i += 20
	while int.from_bytes(c[i:i+4], 'little') != 0x1000000 and i < EDGE_END:
		i += 1
print(edges)
```

```python
import matplotlib.pyplot as plt
dots = [None, (75, 75), (25, 75), (75, 25), (25, 25), (25, 125), (75, 125), (100, 75), (100, 25), (150, 25), (150, 75), (100, 125), (150, 125), (175, 75), (175, 25), (225, 25), (225, 75), (225, 125), (250, 75), (250, 25), (300, 25), (300, 75), (250, 125), (300, 125), (325, 75), (325, 25), (375, 75), (375, 25), (375, 125), (400, 75), (400, 25), (450, 25), (450, 75), (400, 125), (450, 125), (475, 75), (475, 25), (475, 125), (525, 75), (550, 75), (550, 25), (600, 25), (600, 75), (550, 125), (600, 125), (625, 75), (625, 25), (675, 25), (675, 75), (625, 125), (675, 125), (700, 75), (700, 25), (750, 25), (750, 75), (750, 125), (700, 125), (775, 75), (775, 25), (825, 25), (825, 75), (775, 125), (825, 125), (850, 75), (850, 25), (900, 25), (900, 75), (850, 125), (900, 125), (925, 75), (925, 25), (975, 25), (975, 75), (925, 125), (975, 125), (1000, 75), (1000, 25), (1050, 25), (1050, 75), (1000, 125), (1050, 125), (1075, 75), (1075, 25), (1125, 25), (1125, 75), (1125, 125), (1075, 125), (1150, 75), (1150, 25), (1200, 25), (1200, 75), (1200, 125), (1225, 75), (1225, 25), (1225, 125), (1275, 75), (1300, 75), (1300, 25), (1350, 25), (1350, 75), (1300, 125), (1350, 125), (1375, 75), (1375, 25), (1425, 25), (1425, 75), (1375, 125), (1425, 125), (1450, 75), (1450, 25), (1500, 25), (1500, 75), (1450, 125), (1500, 125), (1525, 75), (1525, 25), (1575, 25), (1575, 75), (1525, 125), (1575, 125), (1600, 75)]
edges = [(119, 117), (119, 118), (117, 114), (116, 115), (115, 114), (113, 111), (113, 112), (112, 108), (111, 108), (110, 109), (109, 108), (107, 105), (107, 106), (106, 102), (105, 102), (105, 104), (104, 103), (103, 102), (101, 99), (101, 100), (99, 96), (98, 97), (97, 96), (94, 92), (93, 92), (91, 90), (90, 89), (89, 88), (86, 81), (86, 85), (85, 84), (84, 83), (83, 82), (82, 81), (80, 78), (80, 79), (78, 75), (78, 77), (77, 76), (76, 75), (74, 73), (73, 69), (72, 69), (72, 71), (71, 70), (68, 66), (68, 67), (66, 63), (66, 65), (65, 64), (64, 63), (62, 60), (62, 61), (61, 57), (60, 57), (59, 58), (58, 57), (56, 51), (56, 55), (55, 54), (54, 53), (53, 52), (52, 51), (50, 48), (50, 49), (48, 45), (47, 46), (46, 45), (44, 42), (44, 43), (43, 39), (42, 39), (42, 41), (41, 40), (40, 39), (37, 35), (36, 35), (34, 33), (33, 29), (32, 29), (32, 31), (31, 30), (28, 26), (27, 26), (26, 24), (25, 24), (23, 21), (23, 22), (21, 18), (20, 19), (19, 18), (17, 16), (16, 15), (15, 14), (12, 11), (11, 7), (10, 7), (10, 9), (9, 8), (6, 1), (6, 5), (4, 3), (3, 1), (2, 1)]

for u, v in edges:
	plt.plot([dots[u][0], dots[v][0]], [dots[u][1], dots[v][1]], '-', color='r')

plt.show()
```

这题之所以放在 Reverse 标签内大概是因为最后需要把图翻转 180 度再水平翻转吧。

## ByteKit

给了一个 qemu 镜像和 bios，先看看 getflag.sh

```shell
#!/bin/bash

BYTECTF_INPUT_GUID=93e91ed6-1a7a-46a1-b880-c5d281700ea2
BYTECTF_OUTPUT_GUID=93e91ed6-1a7a-46a1-b880-c5c281700ea2
BYTECTF_INPUT_VAR_FILE="/sys/firmware/efi/efivars/ByteCTFIn-$BYTECTF_INPUT_GUID"
BYTECTF_OUTPUT_VAR_FILE="/sys/firmware/efi/efivars/ByteCTFOut-$BYTECTF_OUTPUT_GUID"

if [ "$1" == "" ]; then
    echo "$0 <your input>"
    exit 1
fi

input=$1
echo "your input is $input"

if [ -f $BYTECTF_OUTPUT_VAR_FILE ]; then
    flag1=$input
    flag2=`cat $BYTECTF_OUTPUT_VAR_FILE | base64 | cut -c -24`
    echo "ByteCTF{$flag1$flag2}"
    chattr -i $BYTECTF_OUTPUT_VAR_FILE
    rm -f $BYTECTF_OUTPUT_VAR_FILE
    exit 0
fi

if [ -f $BYTECTF_INPUT_VAR_FILE ]; then
    chattr -i $BYTECTF_INPUT_VAR_FILE
    rm -f $BYTECTF_INPUT_VAR_FILE
fi

echo -en "\x07\x00\x00\x00$input" | sudo tee $BYTECTF_INPUT_VAR_FILE > /dev/null
echo "system will reboot in 10 seconds"
sh -c "sleep 10; reboot" &
```

根据题目描述，运行这个脚本设置了 ByteCTFIn 之后重启，根据有没有 ByteCTFOut 来判定 flag 是否正确。这里写的是 /efi/efivars，可以判断和 uefi 相关，应该是在 bios.bin 里做的校验。用 UEFI Tools 解包了一下可以发现下面两个有趣的东西：

```
VSS entry       | Auth                  | 00004F64 | 00000055 | C3C482FF | --- 93E91ED6-1A7A-46A1-B880-C5D281700EA2 | ByteCTFIn
File            | DXE driver            |   N/A    | 0001CF4E | 6489F051 | ------ FB08605D-6B57-409B-A195-C67992ECF0EE | ByteKitLoaderDxe
```

dump 出 ByteKitLoaderDxe 之后直接逆向分析，有 ollvm 混淆，crc32 和 smc 的异或混在一起，已经逆了两个题神志不清的我直接忽略了 smc 的那个异或干瞪了好一会啥都没看出来，又因为完全没有接触过 uefi 相关的东西根本不会调试，遂躺床上昏迷成为战犯。赛后经好心人提点知道这个 ollvm 可以直接用 d810 去除（真没想到 2024 年了还有能被完美去除的 ollvm 混淆...）

去除混淆后可以发现是一个简单的异或解密了另一个 module 然后 load 进来执行，里面的逻辑也是简单异或。

```python
key = [0x62, 1, 0x0B, 0x79, 2, 3, 0x74, 3, 7, 0x65, 4, 0x0E, 0x64, 5, 0x0D, 0x61, 6, 0x0A, 0x6E, 7, 0x0F, 0x63, 8, 0x0C, 0x65, 9, 0x0A]
cip = [  0x4B, 0x27, 0x42, 0x55, 0x48, 0x6E, 0x41, 0x29, 0x1F, 0x5E, 
  0x04, 0x04, 0x6B, 0x3E, 0x57, 0x5F, 0x08, 0x07, 0x5F, 0x3A, 
  0x31, 0x17, 0x40, 0x30, 0x5F, 0x7A, 0x75, 0x67, 0x36, 0x36, 
  0x36, 0x36]
for i in range(0, len(key), 3):
	for j in range(key[i+1], key[i+1]+key[i+2]):
		cip[j] ^= key[i]
print(bytearray(cip))
```


