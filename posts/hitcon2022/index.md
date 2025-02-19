# Hitcon2022-Checker Windows驱动文件分析


with Katzebin 就不传附件了

附件有checker.exe和check_drv.sys两个文件

checker.exe逻辑十分简单

```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  HANDLE FileW; // rax
  char *v4; // rcx
  char OutBuffer[4]; // [rsp&#43;40h] [rbp-18h] BYREF
  DWORD BytesReturned; // [rsp&#43;44h] [rbp-14h] BYREF

  FileW = CreateFileW(L&#34;\\\\.\\hitcon_checker&#34;, 0xC0000000, 0, 0i64, 3u, 4u, 0i64);
  qword_140003620 = (__int64)FileW;
  if ( FileW == (HANDLE)-1i64 )
  {
    sub_140001010(&#34;driver not found\n&#34;);
    exit(0);
  }
  OutBuffer[0] = 0;
  DeviceIoControl(FileW, 0x222080u, 0i64, 0, OutBuffer, 1u, &amp;BytesReturned, 0i64);
  v4 = &#34;correct\n&#34;;
  if ( !OutBuffer[0] )
    v4 = &#34;wrong\n&#34;;
  sub_140001010(v4);
  system(&#34;pause&#34;);
  return 0;
}
```

https://www.cnblogs.com/lsh123/p/7354573.html

具体可以参照这篇文章，程序整体逻辑是检测设备`hitcon_checker`并与该设备的驱动交互。可以发现这里的交互操作只有读取，可以知道整体逻辑应该是由`hitcon_checker`设备发送IRP（`I/O Request Package`）包由驱动程序处理，根据处理结果返回正误。

但是我们没有这个设备....

考虑对驱动程序进行分析。找到驱动程序里的dispatcher函数

```
__int64 __fastcall sub_1400011B0(struct _DEVICE_OBJECT *a1, __int64 a2)
{
  ULONG Length; // esi
  PIO_STACK_LOCATION CurrentIrpStackLocation; // rax
  char v7; // cl
  __int64 v8; // rax
  int v9; // ecx

  Length = 0;
  CurrentIrpStackLocation = IoGetCurrentIrpStackLocation((PIRP)a2);
  if ( a1 != DeviceObject )
    return 3221225473i64;
  if ( CurrentIrpStackLocation-&gt;MajorFunction )
  {
    if ( CurrentIrpStackLocation-&gt;MajorFunction == 14 )
    {
      Length = CurrentIrpStackLocation-&gt;Parameters.Read.Length;
      switch ( CurrentIrpStackLocation-&gt;Parameters.Read.ByteOffset.LowPart )
      {
        case 0x222000u:
          sub_1400014D0(0i64);
          byte_140013190[0] = 1;
          break;
        case 0x222010u:
          sub_1400014D0(32i64);
          byte_140013191 = 1;
          break;
        case 0x222020u:
          sub_1400014D0(64i64);
          byte_140013192 = 1;
          break;
        case 0x222030u:
          sub_1400014D0(96i64);
          byte_140013193 = 1;
          break;
        case 0x222040u:
          sub_1400014D0(128i64);
          byte_140013194 = 1;
          break;
        case 0x222050u:
          sub_1400014D0(160i64);
          byte_140013195 = 1;
          break;
        case 0x222060u:
          sub_1400014D0(192i64);
          byte_140013196 = 1;
          break;
        case 0x222070u:
          sub_1400014D0(224i64);
          byte_140013197 = 1;
          break;
        case 0x222080u:
          if ( !Length )
            goto LABEL_15;
          v7 = 1;
          v8 = 0i64;
          while ( byte_140013190[v8] )
          {
            if ( &#43;&#43;v8 &gt;= 8 )
              goto LABEL_21;
          }
          v7 = 0;
LABEL_21:
          if ( v7 )
          {
            v9 = dword_140003000 - 1668573544;
            if ( dword_140003000 == 1668573544 )
              v9 = (unsigned __int16)word_140003004 - 28271;
            **(_BYTE **)(a2 &#43; 24) = v9 == 0;
          }
          else
          {
LABEL_15:
            **(_BYTE **)(a2 &#43; 24) = 0;
          }
          break;
        default:
          break;
      }
    }
  }
  else
  {
    byte_140003170[(_QWORD)PsGetCurrentProcessId()] = 1;
  }
  *(_QWORD *)(a2 &#43; 56) = Length;
  *(_DWORD *)(a2 &#43; 48) = 0;
  IofCompleteRequest((PIRP)a2, 0);
  return 0i64;
}
```

发现每一种IRP包都会对`sub_140001B30`的代码段进行一些修改，然后调用该函数执行对应操作。

考虑通过ida makecode解密后的函数的正常与否爆破8种IRP包的发送顺序。

```python
key = [0x19, 0xBC, 0x8F, 0x82, 0xD0, 0x2C, 0x61, 0x34, 0xC0, 0x9F, 
  0xF6, 0x50, 0xD5, 0xFB, 0x0C, 0x6E, 0xD0, 0xEB, 0xE5, 0xE3, 
  0xCE, 0xB5, 0x4C, 0xCA, 0x45, 0xAA, 0x11, 0xB2, 0x3E, 0x62, 
  0x6F, 0x7D, 0xD0, 0xEB, 0xA9, 0xE3, 0xB2, 0x2F, 0x06, 0x47, 
  0x7C, 0x28, 0xC5, 0xDE, 0xDE, 0x1A, 0x4E, 0xD6, 0xD8, 0x2D, 
  0x93, 0x4F, 0x82, 0x65, 0x64, 0xFD, 0x08, 0x62, 0x4B, 0x87, 
  0x7E, 0x52, 0x47, 0x30, 0xB7, 0xBA, 0xD0, 0x39, 0x68, 0x53, 
  0x50, 0xAB, 0x20, 0xD5, 0xCA, 0x84, 0x26, 0x71, 0x6F, 0x91, 
  0x1B, 0x36, 0x46, 0x11, 0xA5, 0xF1, 0x4E, 0x58, 0x6C, 0x74, 
  0xD4, 0x9C, 0x15, 0xE2, 0x28, 0xD5, 0xD9, 0x0F, 0x3D, 0x83, 
  0xF3, 0xFC, 0xD1, 0x13, 0x1A, 0x62, 0x12, 0x40, 0xAA, 0xEA, 
  0xCD, 0xCB, 0xE1, 0xC6, 0x08, 0x81, 0x98, 0xF6, 0x68, 0x88, 
  0xBE, 0x23, 0xB5, 0x9E, 0x55, 0xB9, 0xE2, 0x7D, 0x5A, 0xDA, 
  0x39, 0x07, 0xF0, 0x2E, 0x32, 0x20, 0x59, 0x56, 0x4C, 0xB4, 
  0x8F, 0x3E, 0x07, 0x61, 0xD9, 0x0F, 0x2D, 0x61, 0xF1, 0x91, 
  0x33, 0x14, 0xCB, 0x49, 0x68, 0xFE, 0x1F, 0xD4, 0x8A, 0xFE, 
  0xE1, 0xC6, 0x18, 0x63, 0x9A, 0x9B, 0x8A, 0x8A, 0x7F, 0x08, 
  0xC3, 0xE8, 0xE1, 0xEC, 0x0B, 0x8F, 0x3B, 0x00, 0x94, 0xA5, 
  0x11, 0xE7, 0x47, 0x66, 0xC4, 0x9F, 0x98, 0x18, 0x70, 0xF0, 
  0x30, 0xF6, 0x94, 0x71, 0xB1, 0x95, 0xD1, 0xF0, 0x6F, 0xB7, 
  0xD9, 0x3D, 0x05, 0x9E, 0xC1, 0x53, 0x33, 0x76, 0x9B, 0x4B, 
  0x69, 0xCA, 0xDE, 0xFD, 0x7D, 0x67, 0xB8, 0x29, 0x2B, 0xC7, 
  0xC5, 0x84, 0x2C, 0xD1, 0x87, 0x87, 0xF1, 0x98, 0x97, 0x74, 
  0xAD, 0x4B, 0x32, 0xF0, 0x4A, 0x51, 0x72, 0xEA, 0x09, 0xF7, 
  0x38, 0xFD, 0x27, 0xBD, 0x1C, 0x52, 0x71, 0x43, 0x95, 0x9C, 
  0x1A, 0x86, 0xF2, 0xC0, 0xF9, 0xF8]
key_ori = [0x40, 0x53, 0x48, 0x83, 0xEC, 0x20, 0x48, 0x8B, 0x05, 0x3B, 
  0x0C, 0x00, 0x00, 0x48, 0x8B, 0xDA, 0x48, 0x8B, 0x4A, 0x10, 
  0x48, 0x39, 0x08, 0x75, 0x37, 0x48, 0x8B, 0x4A, 0x08, 0xFF, 
  0x15, 0x1D]
program = [ 0x80, 0xE9, 0x22, 0x80, 0xF1, 0xAD, 0x0F, 0xB6, 0xC1, 0x6B, 0xC8, 0x11, 0xB8, 0x9E, 0x00, 0x00, 0x00, 0x2A, 0xC1, 0xC3]
def solve(pp, offset):
	x = 0x20*offset
	p = []
	for i in range(len(pp)):
		p.append(pp[i])
	for i in range(16):
		p[i] ^= key[x&#43;i]
	with open(f&#34;chall{offset}&#34;, &#34;wb&#34;) as f:
		for i in range(len(p)):
			f.write(p[i].to_bytes(1, &#39;little&#39;))
	for i in range(16):
		p[i] ^= key[x&#43;i&#43;16]
	print(p)
	return p

for i in range(16):
	program[i] ^= key_ori[i]
for i in range(16):
	program[i] ^= key_ori[16&#43;i]

program = solve(program, 7)
program = solve(program, 2)
program = solve(program, 6)
program = solve(program, 0)
program = solve(program, 1)
program = solve(program, 4)
program = solve(program, 3)
program = solve(program, 5)

orderlis = [7, 2, 6, 0, 1, 4, 3, 5]
for i in range(8):
	if i not in orderlis:
		solve(program, i)
```

解密即可

```python
origin = [0x63, 0x60, 0xA5, 0xB9, 0xFF, 0xFC, 0x30, 0x0A, 0x48, 0xBB, 
  0xFE, 0xFE, 0x32, 0x2C, 0x0A, 0xD6, 0xE6, 0xFE, 0xFE, 0x32, 
  0x2C, 0x0A, 0xD6, 0xBB, 0x4A, 0x4A, 0x32, 0x2C, 0xFC, 0xFF, 
  0x0A, 0xFD, 0xBB, 0xFE, 0x2C, 0xB9, 0x63, 0xD6, 0xB9, 0x62, 
  0xD6, 0x0A, 0x4F]
def sub7(a1):
	return ((8 * a1) | (a1 &gt;&gt; 5)) &amp; 0xFF
def sub2(x):
	return (x ^ 0x26) &amp; 0xFF
def sub6(a1):
	return ((16 * a1) | (a1 &gt;&gt; 4)) &amp; 0xFF
def sub0(x):
	return (x &#43; 55) &amp; 0xFF
def sub1(x):
	return (x&#43;123)&amp;0xFF
def sub4(a1):
	return ((a1 &lt;&lt; 7) | (a1 &gt;&gt; 1)) &amp;0xFF
def sub3(x):
	return (173*x)&amp;0xFF
def sub5(a1):
	return ((4 * a1) | (a1 &gt;&gt; 6))&amp;0xFF

for i in range(len(origin)):
	origin[i] = sub7(origin[i])

for i in range(len(origin)):
	origin[i] = sub2(origin[i])

for i in range(len(origin)):
	origin[i] = sub6(origin[i])

for i in range(len(origin)):
	origin[i] = sub0(origin[i])

for i in range(len(origin)):
	origin[i] = sub1(origin[i])

for i in range(len(origin)):
	origin[i] = sub4(origin[i])

for i in range(len(origin)):
	origin[i] = sub3(origin[i])

for i in range(len(origin)):
	origin[i] = sub5(origin[i])

for i in range(len(origin)):
	print(chr(origin[i]), end=&#34;&#34;)
```



---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/hitcon2022/  

