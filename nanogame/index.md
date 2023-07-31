# 『超高校级的幸运』WMCTF2022-nanoDiamond-rev 抽卡实况


# [Crypto] nanoDiamond-rev

### 题目

```python
# from Crypto.Util.number import *
import string
import secrets
from hashlib import sha256
from random import randint, shuffle, choice

def proof_of_work():
    s = ''.join([secrets.choice(string.digits + string.ascii_letters)
                for _ in range(20)])
    print(f'sha256(XXXX+{s[4:]}) == {sha256(s.encode()).hexdigest()}')
    if input('Give me XXXX: ') != s[:4]:
        exit(1)

ROUND_NUM = 50
PREROUND_NUM = 13
CHEST_NUM = 6

with open('flag', 'r') as f:
    flag = f.read()

white_list = ['==','(',')','0','1','and','or','B0','B1','B2','B3','B4','B5']

def calc(ans, chests, expr):
    B0, B1, B2, B3, B4, B5 = chests
    return ans(eval(expr))

def round():
    chests = [choice((True, False)) for _ in range(CHEST_NUM)]
    print("Six chests lie here, with mimics or treasure hidden inside.")
    print("But don't worry. Skeleton Merchant knows what to do.")
    print("Be careful, Skeleton Merchant can lie twice!")

    truth = lambda r: not not r
    lie = lambda r: not r
    lie_num = randint(0, 2)
    lie_status = [truth] * (PREROUND_NUM - lie_num) + [lie] * lie_num
    shuffle(lie_status)

    for i in range(PREROUND_NUM):
        try:
            question = input('Question: ').strip()
            for word in question.split(' '):
                assert word in white_list, f"({word}) No treasure for dirty hacker!"
            result = calc(lie_status[i], chests, question)
            print(f'Answer: {result}!')
        except Exception as e:
            print("Skeleton Merchant fails to understand your words.")
            print(e)
    print('Now open the chests:')
    return chests == list(map(int, input().strip().split(' ')))


if __name__ == '__main__':

    proof_of_work()

    print('Terraria is a land of adventure! A land of mystery!')
    print('Can you get all the treasure without losing your head?')

    for i in range(ROUND_NUM):
        if not round():
            print('A chest suddenly comes alive and BITE YOUR HEAD OFF.')
            exit(0)
        else:
            print('You take all the treasure safe and sound. Head to the next vault!')

    print(f"You've found all the treasure! {flag}")

```



### WP

首先我们有异或运算：

`r1 xor r2 = ((r1 and r2) == 0 ) and (r1 or r2)`

考虑先询问每个值一次，询问方法类似：

`B0 == 1`

得到每个bool变量的初始值。

由于可能说谎，验证一下，询问：

`B0 xor B1 == 1`

`B2 xor B3 == 1`

`B4 xor B5 == 1`

假设上面的询问与第一轮得到的值有矛盾，则说明A、B、A xor B 中有一个假信息。（有两个假信息概率较小）

此时已经出现一次错误，我们认定后面的回答都是正确的（再次出现假信息概率较小）

考虑再次询问 A xor B：

若答案和之前相同，则认为A xor B正确，询问A可以得到A和B哪个正确，更新A和B的值。

若答案和之前不同则认为A xor B错误，保持A和B值不变。

由于最多可能出现两次矛盾，每次矛盾需要2次询问验证，总询问次数最多为6+3+2+2=13。

但是前面忽略的几种“概率较小”的情况加起来并且在连续进行50轮的情况下出现的概率是非常高的。跑通的概率大概和手游抽卡差不多。

但是不怕，我是欧皇，跑了几百次就出flag了。

```python
from pwn import *
context.log_level='info'
from Crypto.Util.number import *
from pwnlib.util.iters import mbruteforce 
from hashlib import sha256 

from gmpy2 import *
table = string.ascii_letters+string.digits

def passpow():
    io.recvuntil(b"XXXX+")
    suffix = io.recv(16).decode("utf8")
    io.recvuntil(b"== ")
    cipher = io.recvline().strip().decode("utf8")
    gg = 0
    print(suffix)
    print(cipher)
    for i1 in range(len(table)):
        for i2 in range(len(table)):
            for i3 in range(len(table)):
                for i4 in range(len(table)):
                    sss = sha256((table[i1]+table[i2]+table[i3]+table[i4]+suffix).encode()).hexdigest()
                    if sss == cipher:
                        gg = 1
                        io.sendline((table[i1]+table[i2]+table[i3]+table[i4]).encode())
                        break
                if gg == 1:
                  break
            if gg == 1:
                break
        if gg == 1:
            break
    #io.sendline(proof.encode()) 
def Xor(a, b):
    return f"( ( ( {a} and {b} ) == 0 ) and ( {a} or {b} ) )"
def Not(x):
    if x == 1:
        return 0
    else:
        return 1

def solve(a, b, vala, valb):
    io.recvuntil(b"Question: ")
    io.sendline(f'{Xor(f"B{a}", f"B{b}")} == 1'.encode())
    io.recvuntil(b"Answer: ")
    tmp = io.recvline().strip()[:-1]
    if (eval(tmp)) == ((vala ^ valb) == 1):
        return vala, valb, 1
    io.recvuntil(b"Question: ")
    io.sendline(f'{Xor(f"B{a}", f"B{b}")} == 1'.encode())
    io.recvuntil(b"Answer: ")
    tmp2 = io.recvline().strip()[:-1]
    if (eval(tmp2)) == ((vala ^ valb) == 1):
        return vala, valb, 2
    io.recvuntil(b"Question: ")
    io.sendline(f'B{a} == 1'.encode())
    io.recvuntil(b"Answer: ")
    tmp = io.recvline().strip()[:-1]
    if (eval(tmp)) == vala:
        return vala, Not(valb), 3
    else:
        return Not(vala), valb, 3

def exp():
    passpow()
    print("DONEPOW")
    ROUND_NUM = 50
    #io.interactive()
    io.recvuntil(b"Can you get all the treasure without losing your head?")
    for i in range(ROUND_NUM):
        io.recvuntil(b"Be careful, Skeleton Merchant can lie twice!")
        print(f'round = {i}')
        ans = []
        for j in range(6):
            io.recvuntil(b"Question: ")
            io.sendline(f'B{j} == 1'.encode())
            io.recvuntil(b"Answer: ")
            tmp = io.recvline().strip()[:-1]
            if(eval(tmp)):
                ans.append(1)
            else:
                ans.append(0)

        num = 6
        a, b, c = solve(0, 1, ans[0], ans[1])
        num += c
        ans[0] = a
        ans[1] = b

        a, b, c = solve(2, 3, ans[2], ans[3])
        num += c
        ans[2] = a
        ans[3] = b

        a, b, c = solve(4, 5, ans[4], ans[5])
        num += c
        ans[4] = a
        ans[5] = b

        remain = 13 - num
        for j in range(remain):
            io.recvuntil(b"Question: ")
            io.sendline(f'B{j} == 1'.encode())
            io.recvuntil(b"Answer: ")
            tmp = io.recvline().strip()[:-1]


        tosend = str(ans)[1:-1].replace(',','')
        io.recvuntil(b'Now open the chests:\n')
        io.sendline(tosend)

    io.interactive()

while True:
    try:
        io = remote("1.13.154.182", 32664)
        exp()
    except Exception as e:
        print(e)
```


