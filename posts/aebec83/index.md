# EDBG 开发笔记：从0开始用 EBPF 构建“隐身”的调试器


## 前言

本文主要介绍 [eDBG](https://github.com/ShinoLeah/eDBG) 从 0 到 1（也许只是 0.5）的心路历程和设计过程，也许可能可以给大家一点点启发？

## 碎碎念

结束了总计时长将近一年的实习，经历了两次互联网大厂的拷打，从 Android 游戏安全做到风险环境和风控，在随手搞定秋招之后，我终于回到学校开始了我的 gap year（其实就是呆在学校搞搞毕业相关的事情的比较不那么忙的一年吧），正好想着可以顺便糊弄毕业设计，就想把我之前的一些灵机一动实现一下。

由于众所周知的原因，现有的 Android 调试器全都是基于 ptrace 方案的，针对 ptrace 方案的检测非常非常多，每次调试都需要做很多麻烦的绕过（当然大部分时间都是在定位不到或者绕不过去？），用 hook 框架也总是会引入很多不友善的特征，用模拟器的“降维调试”也会直接因为没有合适的传感器数据或者特征文件被识别为风险环境——毕竟在大数据时代，一点风吹草动都会被识别为“离群值”被击毙。

在这个环境下，比较好用的方案就是我最爱用的 [stackplz](https://github.com/SeeFlowerX/stackplz)，这是一个使用 eBPF 来监视程序的辅助工具，由于在一般场景下，被调试的 APP 一般都不会拥有 ROOT 权限，因此针对 eBPF 技术的检测手段极少极少，因此这个工具非常好用。但是美中不足的是，作为一个记录式的辅助工具，和直接进行自由的调试相比，能提供的信息还是有上限的。

这时，比较流行的解决方案是使用 stackplz 注册 uprobe，然后发送信号挂起程序，再用调试器附加进行调试。

&lt;!--more--&gt;

## 雏形

我想，既然我们有可以发送信号的 eBPF 模块，可以暂停和继续程序，**那么我们能不能用这个技术直接做出一个调试器呢？**

众所周知（也许），Android 里加载 eBPF 的大概框架就是有一个 Application，它向内核注册 eBPF 模块，这个模块监听目标程序，然后 Application 和这个模块进行交互来达到监听的目的，具体原理我就不展开赘述了。

eBPF 模块有读取目标程序寄存器的功能，有向目标程序发送信号的接口 `bpf_send_signal`，那么我们可以简单设计出最基本的断点：

- 注册 uprobe 断点
- 断点触发，唤醒 eBPF 程序，eBPF 程序发送 SIGSTOP 暂停程序
- 我们的 Application 收到通知，做一些想做的事情
- Application 向目标程序发送 SIGCONT，程序继续运行。

有了断点的注册和取消，加上亿点点的反汇编和跳转分支预测，我们就能实现单步调试等简单的功能了。

接下来的问题是，我们希望在目标程序被暂停的时候干些什么？

- 读取寄存器：这个很简单，可以直接让 eBPF 程序传回
- 读内存：虽然 eBPF 提供了 `bpf_probe_read_user` 接口，但在用户指定需要读的内存之前，我们永远不知道想要读什么内存。eBPF 程序不像普通的程序那样可以随时被调用，因此我们需要别的方法。

**有没有不引入特征、不侵入程序的方法读写目标程序的内存？**

经常开挂的朋友都知道，有个玩具叫 Cheat Engine，他可以很快地扫描目标程序的内存并且修改，并且只在你需要断点和调试的时候才会使用 ptrace 对目标程序进行附加。

那么，他是怎么做到的呢？实际上，Linux 提供了一个系统调用 `process_vm_readv`，可以远程读取目标内存，并且不会引入特征。相同的，还有`process_vm_writev`，这两个系统调用给了我们远程读写目标内存的能力。

现在我们有控制目标程序运行的方案，也有读取目标程序上下文的方案，到这里我们已经完全可以做出来一个功能完备的调试器了，它甚至可以提供内存写功能来帮你过反调试。

## 执念

虽然只是对现有技术的拼凑组装（Ctrl&#43;C/Ctrl&#43;V），但是现在我们有一个功能完备的调试器了，他引入的特征很少，糊弄我的毕设也完全足够了——毕竟本科生毕业设计的要求总是很低。

但是我总觉得这个调试器有一点不完美的地方——uprobes 会在 `/proc/xxxx/maps` 中引入特征。作为一款为了 ”无痕“”隐身“ 而打造的调试器，这个特征就像一颗老鼠屎一样被放在那里。我觉得，特征只有没有和有的区别，只要能被用户态探测到，我总会觉得我的项目因为这一点特征变得没有意义。

虽然说正经的调试器不干隐藏的活，而且给我的毕设打分的老师们肯定也不会知道我的调试器会引入特征，但是当我把项目 push 到 github 上之后，短短 5 天就收到了 200 星，这大大地激励了我，让我下定决心把这个产品继续打磨完整。

最简单的做法当然是使用 eBPF hook 系统调用，不让目标程序读到这段 maps。但我总觉得这样做不对，我认为调试器本身不应该干扰或者影响程序的运行，即使这样可以藏起这个特征。因此，我开始在内核中寻找一种不修改目标程序的隐藏方法。

## 突破

一个简单的方案是使用基于 perf_event 的硬件断点，但是硬件断点有数量限制（其实这部分我没有仔细研究，但是我觉得硬件断点总是只能设置四五个的样子？），全部改用硬件断点显然不是一个好主意。但是我们有只需要使用一个断点的功能——单步调试。单步调试总是只需要一个断点，因此完全可以使用硬件断点来做这部分功能，那么剩下的问题就是用户设置的断点。

经过研究我取得了一点突破：[eDBG 使用进阶：避免 uprobes 产生可被察觉的特征](https://www.sh1no.icu/posts/28348c4/)

简单来说，**并不是所有指令在被 uprobe 附加的时候都会在 maps 中产生特征，而且这种指令还非常常见——所有跳转指令**。

那么我们就有了新的可能：在跳转指令处使用 uprobe 设置断点，然后使用单步调试功能（或者更快的 `until` 功能）调试到想要的位置，只要这样我们就可以实现完全无法被用户态察觉地调试任何我们想要的位置。

## 总结

至此，一个我认为”完美“的调试器已经完成了。可能我有些代码写得不对引入了一些 bug 或者一些问题，但是至少在理论上，这是一个可以完全”隐身“的调试器。

当然也有可能因为我的见识不足知道的反调试手段不够多导致别的问题，但是至少退一步说，我应该可以拿到毕业证了大概。


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/aebec83/  

