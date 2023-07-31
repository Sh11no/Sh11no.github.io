# 智能合约逆向分析实战 ByteCTF2022-OhMySolidity


## [Reverse] OhMySolidity

题面如下

```
input:
0x608060405234801561001057600080fd5b5061066e806100206000396000f3fe608060405234801561001057600080fd5b50600436106100625760003560e01c806314edb54d1461006757806358f5382e1461009157806393eed093146101c55780639577a145146101ef578063a7f81e6a14610253578063f0407ca71461027d575b600080fd5b61006f6102a7565b604051808263ffffffff1663ffffffff16815260200191505060405180910390f35b61014a600480360360208110156100a757600080fd5b81019080803590602001906401000000008111156100c457600080fd5b8201836020820111156100d657600080fd5b803590602001918460018302840111640100000000831117156100f857600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192905050506102bd565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561018a57808201518184015260208101905061016f565b50505050905090810190601f1680156101b75780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b6101cd61056f565b604051808263ffffffff1663ffffffff16815260200191505060405180910390f35b6102516004803603608081101561020557600080fd5b81019080803563ffffffff169060200190929190803563ffffffff169060200190929190803563ffffffff169060200190929190803563ffffffff169060200190929190505050610584565b005b61025b61060d565b604051808263ffffffff1663ffffffff16815260200191505060405180910390f35b610285610623565b604051808263ffffffff1663ffffffff16815260200191505060405180910390f35b600060049054906101000a900463ffffffff1681565b606080829050600060088251816102d057fe5b06146102db57600080fd5b606081516040519080825280601f01601f1916602001820160405280156103115781602001600182028038833980820191505090505b509050600063deadbeef905060008090505b83518110156105635760008090506000809050600080905060008090505b60048160ff1610156103cd578060030360080260ff16888260ff1687018151811061036857fe5b602001015160f81c60f81b60f81c60ff1663ffffffff16901b830192508060030360080260ff168860048360ff16880101815181106103a357fe5b602001015160f81c60f81b60f81c60ff1663ffffffff16901b820191508080600101915050610341565b5060008090505b60208160ff16101561047f578584019350600060049054906101000a900463ffffffff1660058363ffffffff16901c018483016000809054906101000a900463ffffffff1660048563ffffffff16901b011818830192506000600c9054906101000a900463ffffffff1660058463ffffffff16901c01848401600060089054906101000a900463ffffffff1660048663ffffffff16901b0118188201915080806001019150506103d4565b5060008090505b60048160ff1610156105545760ff8160030360080260ff168463ffffffff16901c1660f81b878260ff168701815181106104bc57fe5b60200101907effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916908160001a90535060ff8160030360080260ff168363ffffffff16901c1660f81b8760048360ff168801018151811061051857fe5b60200101907effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916908160001a9053508080600101915050610486565b50505050600881019050610323565b50819350505050919050565b6000809054906101000a900463ffffffff1681565b836000806101000a81548163ffffffff021916908363ffffffff16021790555082600060046101000a81548163ffffffff021916908363ffffffff16021790555081600060086101000a81548163ffffffff021916908363ffffffff160217905550806000600c6101000a81548163ffffffff021916908363ffffffff16021790555050505050565b600060089054906101000a900463ffffffff1681565b6000600c9054906101000a900463ffffffff168156fea265627a7a72315820c500ad9e15f8594ce1140fdf04f71759a549b8a033f78b149472bb00f68975a964736f6c63430005110032
output:
None

input:
0x9577a1450000000000000000000000000000000000000000000000000000000012345678000000000000000000000000000000000000000000000000000000008765432100000000000000000000000000000000000000000000000000000000aabbccdd0000000000000000000000000000000000000000000000000000000044332211
output:
None

input(broken):
0x58f5382e...
output:
0xa625e97482f83d2b7fc5125763dcbbffd8115b208c4754eee8711bdfac9e3377622bbf0cbb785e612b82c7f5143d5333
```



根据题目提示和开头60806040可以知道是一个Solidity字节码的逆向。Solidity语言是在区块链的智能合约部署中被广泛使用的语言之一。

由于之前有接触过智能合约字节码逆向我们很快就找到了反编译的工具。

[Online Solidity Decompiler (ethervm.io)](https://ethervm.io/decompile/)

```
contract Contract {
    function main() {
        memory[0x40:0x60] = 0x80;
        var var0 = msg.value;
    
        if (var0) { revert(memory[0x00:0x00]); }
    
        memory[0x00:0x066e] = code[0x20:0x068e];
        return memory[0x00:0x066e];
    }
}
```

反编译结果明显短于字节码长度。观察到`memory[0x00:0x066e] = code[0x20:0x068e];`行，推测是把0x20部分代码复制到memory内继续执行。

实际上区块链智能合约分为部署合约和上链合约两部分，上链合约短于智能合约。同时，我们在0x20个字节后又发现了魔数60806040，尝试删除前缀0x20字节重新反编译。

```
contract Contract {
    function main() {
        memory[0x40:0x60] = 0x80;
        var var0 = msg.value;
    
        if (var0) { revert(memory[0x00:0x00]); }
    
        if (msg.data.length < 0x04) { revert(memory[0x00:0x00]); }
    
        var0 = msg.data[0x00:0x20] >> 0xe0;
    
        if (var0 == 0x14edb54d) {
            // Dispatch table entry for k1()
            var var1 = 0x006f;
            var var2 = k1();
            var temp0 = memory[0x40:0x60];
            memory[temp0:temp0 + 0x20] = var2 & 0xffffffff;
            var temp1 = memory[0x40:0x60];
            return memory[temp1:temp1 + (temp0 + 0x20) - temp1];
        } else if (var0 == 0x58f5382e) {
            // Dispatch table entry for challenge(string)
            var1 = 0x014a;
            var2 = 0x04;
            var var3 = msg.data.length - var2;
        
            if (var3 < 0x20) { revert(memory[0x00:0x00]); }
        
            var1 = challenge(var2, var3);
            var temp2 = memory[0x40:0x60];
            var2 = temp2;
            var3 = var2;
            var temp3 = var3 + 0x20;
            memory[var3:var3 + 0x20] = temp3 - var3;
            var temp4 = var1;
            memory[temp3:temp3 + 0x20] = memory[temp4:temp4 + 0x20];
            var var4 = temp3 + 0x20;
            var var5 = temp4 + 0x20;
            var var6 = memory[temp4:temp4 + 0x20];
            var var7 = var6;
            var var8 = var4;
            var var9 = var5;
            var var10 = 0x00;
        
            if (var10 >= var7) {
            label_018A:
                var temp5 = var6;
                var4 = temp5 + var4;
                var5 = temp5 & 0x1f;
            
                if (!var5) {
                    var temp6 = memory[0x40:0x60];
                    return memory[temp6:temp6 + var4 - temp6];
                } else {
                    var temp7 = var5;
                    var temp8 = var4 - temp7;
                    memory[temp8:temp8 + 0x20] = ~(0x0100 ** (0x20 - temp7) - 0x01) & memory[temp8:temp8 + 0x20];
                    var temp9 = memory[0x40:0x60];
                    return memory[temp9:temp9 + (temp8 + 0x20) - temp9];
                }
            } else {
            label_0178:
                var temp10 = var10;
                memory[var8 + temp10:var8 + temp10 + 0x20] = memory[var9 + temp10:var9 + temp10 + 0x20];
                var10 = temp10 + 0x20;
            
                if (var10 >= var7) { goto label_018A; }
                else { goto label_0178; }
            }
        } else if (var0 == 0x93eed093) {
            // Dispatch table entry for 0x93eed093 (unknown)
            var1 = 0x01cd;
            var2 = func_056F();
            var temp11 = memory[0x40:0x60];
            memory[temp11:temp11 + 0x20] = var2 & 0xffffffff;
            var temp12 = memory[0x40:0x60];
            return memory[temp12:temp12 + (temp11 + 0x20) - temp12];
        } else if (var0 == 0x9577a145) {
            // Dispatch table entry for 0x9577a145 (unknown)
            var1 = 0x0251;
            var2 = 0x04;
            var3 = msg.data.length - var2;
        
            if (var3 < 0x80) { revert(memory[0x00:0x00]); }
        
            func_0205(var2, var3);
            stop();
        } else if (var0 == 0xa7f81e6a) {
            // Dispatch table entry for k2()
            var1 = 0x025b;
            var2 = k2();
            var temp13 = memory[0x40:0x60];
            memory[temp13:temp13 + 0x20] = var2 & 0xffffffff;
            var temp14 = memory[0x40:0x60];
            return memory[temp14:temp14 + (temp13 + 0x20) - temp14];
        } else if (var0 == 0xf0407ca7) {
            // Dispatch table entry for 0xf0407ca7 (unknown)
            var1 = 0x0285;
            var2 = func_0623();
            var temp15 = memory[0x40:0x60];
            memory[temp15:temp15 + 0x20] = var2 & 0xffffffff;
            var temp16 = memory[0x40:0x60];
            return memory[temp16:temp16 + (temp15 + 0x20) - temp16];
        } else { revert(memory[0x00:0x00]); }
    }
    
    function challenge(var arg0, var arg1) returns (var r0) {
        var temp0 = arg0;
        var temp1 = temp0 + arg1;
        arg1 = temp0;
        arg0 = temp1;
        var var0 = arg1 + 0x20;
        var var1 = msg.data[arg1:arg1 + 0x20];
    
        if (var1 > 0x0100000000) { revert(memory[0x00:0x00]); }
    
        var temp2 = arg1 + var1;
        var1 = temp2;
    
        if (var1 + 0x20 > arg0) { revert(memory[0x00:0x00]); }
    
        var temp3 = var1;
        var temp4 = msg.data[temp3:temp3 + 0x20];
        var1 = temp4;
        var var2 = var0;
        var0 = temp3 + 0x20;
    
        if ((var1 > 0x0100000000) | (var0 + var1 > arg0)) { revert(memory[0x00:0x00]); }
    
        var temp5 = var1;
        var temp6 = memory[0x40:0x60];
        memory[0x40:0x60] = temp6 + (temp5 + 0x1f) / 0x20 * 0x20 + 0x20;
        memory[temp6:temp6 + 0x20] = temp5;
        var temp7 = temp6 + 0x20;
        memory[temp7:temp7 + temp5] = msg.data[var0:var0 + temp5];
        memory[temp7 + temp5:temp7 + temp5 + 0x20] = 0x00;
        arg0 = temp6;
        arg1 = 0x60;
        var0 = arg0;
        var1 = 0x00;
        var2 = 0x08;
        var var3 = memory[var0:var0 + 0x20];
    
        if (!var2) { assert(); }
    
        if (var3 % var2 != var1) { revert(memory[0x00:0x00]); }
    
        var1 = 0x60;
        var temp8 = memory[var0:var0 + 0x20];
        var temp9 = memory[0x40:0x60];
        var3 = temp8;
        var2 = temp9;
        memory[var2:var2 + 0x20] = var3;
        memory[0x40:0x60] = var2 + (var3 + 0x1f & ~0x1f) + 0x20;
    
        if (!var3) {
            var1 = var2;
            var2 = 0xdeadbeef;
            var3 = 0x00;
        
            if (var3 >= memory[var0:var0 + 0x20]) {
            label_0563:
                return var1;
            } else {
            label_032D:
                var var4 = 0x00;
                var var5 = 0x00;
                var var6 = 0x00;
                var var7 = 0x00;
            
                if (var7 & 0xff >= 0x04) {
                label_03CD:
                    var7 = 0x00;
                
                    if (var7 & 0xff >= 0x20) {
                    label_047F:
                        var7 = 0x00;
                    
                        if (var7 & 0xff >= 0x04) {
                        label_0554:
                            var3 = var3 + 0x08;
                        
                            if (var3 >= memory[var0:var0 + 0x20]) { goto label_0563; }
                            else { goto label_032D; }
                        } else {
                        label_0493:
                            var temp10 = var7;
                            var var8 = (((var5 & 0xffffffff) >> (0x03 - temp10 * 0x08 & 0xff)) & 0xff) << 0xf8;
                            var var9 = var1;
                            var var10 = var3 + (temp10 & 0xff);
                        
                            if (var10 >= memory[var9:var9 + 0x20]) { assert(); }
                        
                            memory[var10 + 0x20 + var9:var10 + 0x20 + var9 + 0x01] = byte(var8 & ~0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 0x00);
                            var temp11 = var7;
                            var8 = (((var6 & 0xffffffff) >> (0x03 - temp11 * 0x08 & 0xff)) & 0xff) << 0xf8;
                            var9 = var1;
                            var10 = var3 + (temp11 & 0xff) + 0x04;
                        
                            if (var10 >= memory[var9:var9 + 0x20]) { assert(); }
                        
                            memory[var10 + 0x20 + var9:var10 + 0x20 + var9 + 0x01] = byte(var8 & ~0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 0x00);
                            var7 = var7 + 0x01;
                        
                            if (var7 & 0xff >= 0x04) { goto label_0554; }
                            else { goto label_0493; }
                        }
                    } else {
                    label_03E1:
                        var temp12 = var4 + var2;
                        var4 = temp12;
                        var temp13 = var6;
                        var temp14 = var5 + (((temp13 & 0xffffffff) << 0x04) + (storage[0x00] & 0xffffffff) ~ temp13 + var4 ~ ((temp13 & 0xffffffff) >> 0x05) + (storage[0x00] / 0x0100 ** 0x04 & 0xffffffff));
                        var5 = temp14;
                        var6 = temp13 + (((var5 & 0xffffffff) << 0x04) + (storage[0x00] / 0x0100 ** 0x08 & 0xffffffff) ~ var5 + var4 ~ ((var5 & 0xffffffff) >> 0x05) + (storage[0x00] / 0x0100 ** 0x0c & 0xffffffff));
                        var7 = var7 + 0x01;
                    
                        if (var7 & 0xff >= 0x20) { goto label_047F; }
                        else { goto label_03E1; }
                    }
                } else {
                label_034E:
                    var temp15 = var7;
                    var8 = 0x03 - temp15 * 0x08 & 0xff;
                    var9 = var0;
                    var10 = var3 + (temp15 & 0xff);
                
                    if (var10 >= memory[var9:var9 + 0x20]) { assert(); }
                
                    var5 = var5 + (((((memory[var10 + 0x20 + var9:var10 + 0x20 + var9 + 0x20] >> 0xf8) << 0xf8) >> 0xf8) & 0xff) << var8);
                    var temp16 = var7;
                    var8 = 0x03 - temp16 * 0x08 & 0xff;
                    var9 = var0;
                    var10 = var3 + (temp16 & 0xff) + 0x04;
                
                    if (var10 >= memory[var9:var9 + 0x20]) { assert(); }
                
                    var6 = var6 + (((((memory[var10 + 0x20 + var9:var10 + 0x20 + var9 + 0x20] >> 0xf8) << 0xf8) >> 0xf8) & 0xff) << var8);
                    var7 = var7 + 0x01;
                
                    if (var7 & 0xff >= 0x04) { goto label_03CD; }
                    else { goto label_034E; }
                }
            }
        } else {
            var temp17 = var3;
            memory[var2 + 0x20:var2 + 0x20 + temp17] = code[code.length:code.length + temp17];
            var1 = var2;
            var2 = 0xdeadbeef;
            var3 = 0x00;
        
            if (var3 >= memory[var0:var0 + 0x20]) { goto label_0563; }
            else { goto label_032D; }
        }
    }
    
    function func_0205(var arg0, var arg1) {
        var temp0 = arg0;
        var temp1 = temp0 + 0x20;
        arg0 = msg.data[temp0:temp0 + 0x20] & 0xffffffff;
        var temp2 = temp1 + 0x20;
        arg1 = msg.data[temp1:temp1 + 0x20] & 0xffffffff;
        var var0 = msg.data[temp2:temp2 + 0x20] & 0xffffffff;
        var var1 = msg.data[temp2 + 0x20:temp2 + 0x20 + 0x20] & 0xffffffff;
        storage[0x00] = (arg0 & 0xffffffff) | (storage[0x00] & ~0xffffffff);
        storage[0x00] = (arg1 & 0xffffffff) * 0x0100 ** 0x04 | (storage[0x00] & ~(0xffffffff * 0x0100 ** 0x04));
        storage[0x00] = (var0 & 0xffffffff) * 0x0100 ** 0x08 | (storage[0x00] & ~(0xffffffff * 0x0100 ** 0x08));
        storage[0x00] = (var1 & 0xffffffff) * 0x0100 ** 0x0c | (storage[0x00] & ~(0xffffffff * 0x0100 ** 0x0c));
    }
    
    function k1() returns (var r0) { return storage[0x00] / 0x0100 ** 0x04 & 0xffffffff; }
    
    function func_056F() returns (var r0) { return storage[0x00] & 0xffffffff; }
    
    function k2() returns (var r0) { return storage[0x00] / 0x0100 ** 0x08 & 0xffffffff; }
    
    function func_0623() returns (var r0) { return storage[0x00] / 0x0100 ** 0x0c & 0xffffffff; }
}


```

观察到main()部分包含对var0的一系列判断与分发，猜测var0是标识操作类型的数据。同时在给定的input里发现相应前缀9577a145和58f5382e。

首先观察分析9577a145操作，不难发现是把4个4字节整数拼接在一起存入storage[]中。

58f5382e操作对应challenge，推测是将flag加密后输出密文。

```
var temp14 = var5 + (((temp13 & 0xffffffff) << 0x04) + (storage[0x00] & 0xffffffff) ~ temp13 + var4 ~ ((temp13 & 0xffffffff) >> 0x05) + (storage[0x00] / 0x0100 ** 0x04 & 0xffffffff));
var6 = temp13 + (((var5 & 0xffffffff) << 0x04) + (storage[0x00] / 0x0100 ** 0x08 & 0xffffffff) ~ var5 + var4 ~ ((var5 & 0xffffffff) >> 0x05) + (storage[0x00] / 0x0100 ** 0x0c & 0xffffffff));
```

根据经验发现TEA加密特征，key是9577a145操作输入的四个数，delta是`var2=0xdeadbeef`。

直接写解密脚本梭哈，用前8个字节成功解出flag头，继续解密拿到flag。

