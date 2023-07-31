# 强网杯2022 - GameMaster


打开是一个德扑小游戏，根据已知信息找开源代码。

https://github.com/XanderUZZZER/Blackjack-master

比较关心的是原开源代码中没有的对gamemessage文件的处理，可以注意到一个类似作弊码的goldFunc函数。

整理一下删除没用的部分。

```c#
private static void goldFunc(ArrayList input, Blackjack.Game game)
  {
    if (memcmp(input, "AQLMP6579", 9))
    {
      if (memcmp1(input, "MF3K", 4))
      {
        try
        {
          game.Player.Bet -= 22m;
          for (int i = 0; i < memory.Length; i++)
          {
            memory[i] ^= 34;
          }
          Environment.SetEnvironmentVariable("AchivePoint1", game.Player.Balance.ToString());
          return;
        }
        catch
        {
          return;
        }
      }
    }
    else if (memcmp(input, "Z5M0G6P16", 9))
    {
      if (memcmp1(input, "EEPW", 4))
      {
        try
        {
          game.Player.Balance += 175m;
          byte[] key = new byte[16]
          {
            66, 114, 97, 105, 110, 115, 116, 111, 114, 109,
            105, 110, 103, 33, 33, 33
          };
          RijndaelManaged rijndaelManaged = new RijndaelManaged();
          rijndaelManaged.Key = key;
          rijndaelManaged.Mode = CipherMode.ECB;
          rijndaelManaged.Padding = PaddingMode.Zeros;
          ICryptoTransform cryptoTransform = rijndaelManaged.CreateDecryptor();
          m = cryptoTransform.TransformFinalBlock(memory, 0, memory.Length);
          Environment.SetEnvironmentVariable("AchivePoint2", game.Player.Balance.ToString());
          return;
        }
        catch
        {
          return;
        }
      }
    }
    else
    {
      if (!memcmp(input, "D253Y5J0Y", 9))
      {
        return;
      }
      if (memcmp1(input, "6VD6", 4))
      {
        try
        {
          game.Player.Balance -= 27m;
          Environment.SetEnvironmentVariable("AchivePoint3", game.Player.Balance.ToString());
          BinaryFormatter binaryFormatter = new BinaryFormatter();
          MemoryStream serializationStream = new MemoryStream(m);
          binaryFormatter.Deserialize(serializationStream);
          return;
        }
        catch
        {
          return;
        }
      }
    }
  }
```

复制出来直接跑，dump处理后的gamemessage文件。

```c#
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using System.Security.Cryptography;

namespace ConsoleApp1
{
    class Program
    {
        public static byte[] memory;
        public static byte[] m;
        static void Main(string[] args)
        {
            FileStream fileStream = File.OpenRead("gamemessage");
            int num = (int)fileStream.Length;
            memory = new byte[num];
            fileStream.Position = 0L;
            fileStream.Read(memory, 0, num);
            for (int i = 0; i < memory.Length; i++)
            {
                memory[i] ^= 34;
            }
            byte[] key = new byte[16]
             {
                66, 114, 97, 105, 110, 115, 116, 111, 114, 109,
             105, 110, 103, 33, 33, 33
           };
            RijndaelManaged rijndaelManaged = new RijndaelManaged();
            rijndaelManaged.Key = key;
            rijndaelManaged.Mode = CipherMode.ECB;
            rijndaelManaged.Padding = PaddingMode.Zeros;
            ICryptoTransform cryptoTransform = rijndaelManaged.CreateDecryptor();
            m = cryptoTransform.TransformFinalBlock(memory, 0, memory.Length);
            BinaryFormatter binaryFormatter = new BinaryFormatter();
            MemoryStream serializationStream = new MemoryStream(m);
						binaryFormatter.Deserialize(serializationStream);
            fileStream = File.OpenWrite("gamemessage2");
            serializationStream.WriteTo(fileStream);
        }
    }
}
```

这里反序列化之后的对象读取有些困难，考虑直接读序列化后写入文件的对象。

打开没东西，但是 Strings 可以发现一些令人在意的字符串。

本来以为要读取反序列化后的C#对象，后来根据Strings得到的信息直接在序列化后的对象里 binwalk 出来另一个PE文件。

**逆向题这么出你还不如放去misc，一点逻辑没有你出你妈呢，纯纯恶心人浪费时间。**

继续逆向得到的 binwalk 文件，令人在意的大概就是以下函数。

```C#
public T1()
{
	try
	{
		string text = null;
		string text2 = null;
		string text3 = null;
		text = Environment.GetEnvironmentVariable("AchivePoint1");
		text2 = Environment.GetEnvironmentVariable("AchivePoint2");
		text3 = Environment.GetEnvironmentVariable("AchivePoint3");
		if (text == null || text2 == null || text3 == null)
		{
			return;
		}
		ulong num = ulong.Parse(text);
		ulong num2 = ulong.Parse(text2);
		ulong num3 = ulong.Parse(text3);
		ulong[] array = new ulong[3];
		byte[] array2 = new byte[40];
		byte[] array3 = new byte[40];
		byte[] array4 = new byte[12];
		byte[] first = new byte[40]
		{
			101, 5, 80, 213, 163, 26, 59, 38, 19, 6,
			173, 189, 198, 166, 140, 183, 42, 247, 223, 24,
			106, 20, 145, 37, 24, 7, 22, 191, 110, 179,
			227, 5, 62, 9, 13, 17, 65, 22, 37, 5
		};
		byte[] array5 = new byte[19]
		{
			60, 100, 36, 86, 51, 251, 167, 108, 116, 245,
			207, 223, 40, 103, 34, 62, 22, 251, 227
		};
		array[0] = num;
		array[1] = num2;
		array[2] = num3;
		Check1(array[0], array[1], array[2], array2);
		if (first.SequenceEqual(array2))
		{
			ParseKey(array, array4);
			for (int i = 0; i < array5.Length; i++)
			{
				array5[i] = (byte)(array5[i] ^ array4[i % array4.Length]);
			}
			MessageBox.Show("flag{" + Encoding.Default.GetString(array5) + "}", "Congratulations!", MessageBoxButtons.OK);
		}
	}
	catch (Exception)
	{
	}
}
private static void Check1(ulong x, ulong y, ulong z, byte[] KeyStream)
{
	int num = -1;
	for (int i = 0; i < 320; i++)
	{
		x = (((x >> 29) ^ (x >> 28) ^ (x >> 25) ^ (x >> 23)) & 1) | (x << 1);
		y = (((y >> 30) ^ (y >> 27)) & 1) | (y << 1);
		z = (((z >> 31) ^ (z >> 30) ^ (z >> 29) ^ (z >> 28) ^ (z >> 26) ^ (z >> 24)) & 1) | (z << 1);
		if (i % 8 == 0)
		{
			num++;
		}
		KeyStream[num] = (byte)((KeyStream[num] << 1) | (uint)(((z >> 32) & 1 & ((x >> 30) & 1)) ^ ((((z >> 32) & 1) ^ 1) & ((y >> 31) & 1))));
	}
}
private static void ParseKey(ulong[] L, byte[] Key)
{
	for (int i = 0; i < 3; i++)
	{
		for (int j = 0; j < 4; j++)
		{
			Key[i * 4 + j] = (byte)((L[i] >> j * 8) & 0xFF);
		}
	}
}
```

逻辑是Check了三个数， 成功Check之后利用这三个数当作key解密输出flag。

直接用z3solver解一下这三个数就做完了。

```python
from z3 import *
x = BitVec('x', 64)
y = BitVec('y', 64)
z = BitVec('z', 64)
KeyStream = [101, 5, 80, 213, 163, 26, 59, 38, 19, 6,
			173, 189, 198, 166, 140, 183, 42, 247, 223, 24,
			106, 20, 145, 37, 24, 7, 22, 191, 110, 179,
			227, 5, 62, 9, 13, 17, 65, 22, 37, 5]
num = -1
sol = Solver()
for i in range(320):
	x = (((x >> 29) ^ (x >> 28) ^ (x >> 25) ^ (x >> 23)) & 1) | (x << 1)
	y = (((y >> 30) ^ (y >> 27)) & 1) | (y << 1)
	z = (((z >> 31) ^ (z >> 30) ^ (z >> 29) ^ (z >> 28) ^ (z >> 26) ^ (z >> 24)) & 1) | (z << 1)
	if i % 8 == 0:
		if i != 0:
			sol.add(RR == KeyStream[num])
		num += 1
		RR = 0
	RR = ((RR << 1) | (((z >> 32) & 1 & ((x >> 30) & 1)) ^ ((((z >> 32) & 1) ^ 1) & ((y >> 31) & 1)))) & 255
print("kokodayo")
print(sol.check())
print(sol.model())
```

```python
L = []
y = 868387187
x = 156324965
z = 3131229747
L.append(x)
L.append(y)
L.append(z)
Key = []
for i in range(3):
	for j in range(4):
		Key.append((L[i] >> j * 8) & 0xFF)
cip = [60, 100, 36, 86, 51, 251, 167, 108, 116, 245, 207, 223, 40, 103, 34, 62, 22, 251, 227]

for i in range(len(cip)):
	cip[i] ^= Key[i % len(Key)]

for i in range(len(cip)):
	print(chr(cip[i]))
```


