# 基于eBPF的安卓CLI调试器——eDBG


## 简介

eDBG 是一款基于 eBPF 技术实现的调试工具，为强对抗场景下的安卓 native 逆向工作打造，提供调试器应有的基本功能，在调试时**不产生任何附加到目标进程的行为**，不使用传统的调试方案，调试器与被调试程序**相互独立**，仅各自与内核产生交互行为，难以被目标进程调试或干扰。

除此之外，eDBG 和被调试程序运行状态互不干扰，断点注册不基于运行时地址，即使一方意外退出或重启，另一方也依旧能正常工作。

eDBG 的使用方式与 gdb 的使用方式几乎相同，无需学习便可直接上手使用。

项目地址：[https://github.com/ShinoLeah/eDBG](https://github.com/ShinoLeah/eDBG)

&lt;!--more--&gt;

## 主要功能

主要支持的功能如下：

- 断点：基于 uprobes 功能实现，在断点处可暂停程序并且读取任意想要的上下文。
- 单步调试：支持步入或步过。
- 内存读写：在断点触发时可以读取任意地址内存，也可以自由写入任意有写权限的地址。
- 线程过滤：你可以仅调试一个或多个想要的线程。
- 符号解析、反汇编等其他调试器应该有的功能。

支持的 gdb 指令列表：`break / continue / step / next / finish  / until / examine / display / quit / list / info / thread`

额外的，你可以使用 `write` 指令写入内存，`set` 指令为指定的地址标注你的自定义符号。

eDBG 也支持将你的进度保存到文件或读取工程文件，以便下一次调试。

详细的使用方式请移步：https://github.com/ShinoLeah/eDBG/blob/main/README.md

## 运行环境

- 目前仅支持 ARM64 架构的 Android 系统，需要 ROOT 权限，推荐搭配 [KernelSU](https://github.com/tiann/KernelSU) 使用
- 系统内核版本5.10&#43; （可执行`uname -r`查看）

## 功能演示

整体的界面设计和信息展示参考了 [pwndbg](https://github.com/pwndbg/pwndbg)，会在断点处自动分析当前代码和寄存器信息，当然你可以在选项里关掉这些显示。

![](https://github.com/ShinoLeah/eDBG/blob/main/demo.png?raw=true)

## 进阶使用

[eDBG 使用进阶：避免 uprobes 产生可被察觉的特征](https://www.sh1no.icu/posts/28348c4/)

## 其他

本项目主要受到 [stackplz](https://github.com/SeeFlowerX/stackplz) 启发，在实际逆向工作中我常常使用 stackplz 辅助 ida 进行动态调试，但常常被堆积如山的反调试手段或蜜罐打得鼻青脸肿...(菜菜)，因此突发奇想将 eBPF 技术直接用于打造一个调试器，虽然比 ida 缺少了图形化界面和反编译（但是现在的 app 还有可以直接 F5 的吗），但是我认为功能也足够作为一个逆向辅助工具进行日常使用。

喜欢的话可以赏个小星星 QAQ → [https://github.com/ShinoLeah/eDBG](https://github.com/ShinoLeah/eDBG)


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/74a6f54/  

