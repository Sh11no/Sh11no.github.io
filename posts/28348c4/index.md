# EDBG 使用进阶：避免 Uprobes 产生可被察觉或检测的特征


## uprobes 特征

目前我接触过的针对 uprobes 的检测手段无非两种：

1. 扫描 BRK 指令
2. 检查 `/proc/pid/maps`中是否含有`[uprobes]`特征

其中第一种检测方案在实际 APP 中几乎不可行——**运行时**的完整性校验会带来巨大的时间开销，正常的 APP 基本无法容忍这种开销， 而对于 app 运行前的整体完整性校验，只需要稍晚附加 uprobes 便能直接绕过，因此本文不讨论这种探测方式。

主要令人担心的是第二种：在使用 uprobes 时，会在`/proc/pid/maps`中产生类似 `7ffffff000-80000000000 --xp 00000000 00:00 0    [uprobes]`的字样，如果你有针对这部分检测的魔改 ROM 或者你会使用 eBPF 对 open 和 read 系统调用进行修改，那你可以直接跳过本文内容。

但是，这种特征是怎么产生的？它在 uprobes 触发时总是会产生吗？**答案是否定的**。具体内容得分析一下这部分的源码。

本文在 ARM64 安卓内核版本 5.15.94 下测试，旧版本可能有所不同。

省流可以直接看后面的总结。

&lt;!--more--&gt;

## 分析

uprobes 事件被触发时，首先会执行这个 uprobe 的处理程序，这部分我们并不关心，重点是在执行 eBPF 程序之后。在网络上搜索资料可以简单得知该特征的大致产生原因：

&gt; 内核创建了一个特殊的内存映射，称为 `[uprobes]`，用于执行原始指令

通过查阅源码可知，这个特征产生于`pre_ssout()`，这个函数的作用是**准备对被探测指令进行单步执行**，由于原指令被替换成 BRK 指令，因此需要分配出一段新的空间来执行原指令。

细节产生原因参考：https://www.cnxct.com/defeating-ebpf-uprobe-monitoring

在执行完原指令后，内核需要将当前 PC 指针恢复到正确的位置。如果是非跳转指令，就需要设置到 PC&#43;4，否则则需要设置到跳转的目标位置。

也就是说大概的执行流程是：

1. 执行 uprobe 处理程序
2. 执行原指令
3. 预测并设置 PC

在这里，我产生了一个大胆的猜想：

**如果设置 uprobe 的位置是一条会改变 PC 指针的指令 (B / CBZ / RET 等)，那么内核将会在第 3 步中预测正确的 PC 指令。此时，第 2 步中的“执行原指令”是否还需要被处理？**

我验证了多次，在跳转指令上设置 uprobe 断点，在 maps 中均无法找到 [uprobes] 特征。也就是说，答案是肯定的。我们在内核中也可以找到相应的验证：

```cpp
static void handle_swbp(struct pt_regs *regs)
{
	//... 不重要的预处理

	handler_chain(uprobe, regs); // 执行 uprobes 处理程序

	if (arch_uprobe_skip_sstep(&amp;uprobe-&gt;arch, regs))
		goto out;

	if (!pre_ssout(uprobe, regs, bp_vaddr)) // 会在 /proc/xxx/maps 中产生 uprobes 特征的函数
		return;

	/* arch_uprobe_skip_sstep() succeeded, or restart if can&#39;t singlestep */
out:
	put_uprobe(uprobe);
}
```

可以看到，有一个名为 `arch_uprobe_skip_sstep` 的函数，当这个函数返回 `true` 时，`pre_ssout` 将会被跳过，此时我们的 uprobe 断点在无法扫描运行代码的前提下**可以做到真正的无痕**。

这个函数的定义根据架构有所不同，但我们进行 Android 相关的逆向一般都是在 ARM64 架构的系统下，因此可以找到这部分[源码](https://elixir.bootlin.com/linux/v5.15.94/source/arch/arm64/kernel/probes/uprobes.c#L103)。

```cpp
bool arch_uprobe_skip_sstep(struct arch_uprobe *auprobe, struct pt_regs *regs)
{
	probe_opcode_t insn;
	unsigned long addr;

	if (!auprobe-&gt;simulate)
		return false;

	insn = *(probe_opcode_t *)(&amp;auprobe-&gt;insn[0]);
	addr = instruction_pointer(regs);

	if (auprobe-&gt;api.handler)
		auprobe-&gt;api.handler(insn, addr, regs);

	return true;
}
```

只需要 `auprobe-&gt;simulate` 被触发，我们就可以跳过会产生特征的 `pre_ssout`。这个参数在 `arch_uprobe_analyze_insn` 中被设定。

```c&#43;&#43;
int arch_uprobe_analyze_insn(struct arch_uprobe *auprobe, struct mm_struct *mm,
		unsigned long addr)
{
	probe_opcode_t insn;

	/* TODO: Currently we do not support AARCH32 instruction probing */
	if (mm-&gt;context.flags &amp; MMCF_AARCH32)
		return -EOPNOTSUPP;
	else if (!IS_ALIGNED(addr, AARCH64_INSN_SIZE))
		return -EINVAL;

	insn = *(probe_opcode_t *)(&amp;auprobe-&gt;insn[0]);

	switch (arm_probe_decode_insn(insn, &amp;auprobe-&gt;api)) {
	case INSN_REJECTED:
		return -EINVAL;

	case INSN_GOOD_NO_SLOT:
		auprobe-&gt;simulate = true;
		break;

	default:
		break;
	}

	return 0;
}
```

那么，什么样的指令是 `INSN_GOOD_NO_SLOT` 的指令呢？

```c&#43;&#43;
enum probe_insn __kprobes
arm_probe_decode_insn(probe_opcode_t insn, struct arch_probe_insn *api)
{
	/*
	 * Instructions reading or modifying the PC won&#39;t work from the XOL
	 * slot.
	 */
	if (aarch64_insn_is_steppable(insn))
		return INSN_GOOD;

	if (aarch64_insn_is_bcond(insn)) {
		api-&gt;handler = simulate_b_cond;
	} else if (aarch64_insn_is_cbz(insn) ||
	    aarch64_insn_is_cbnz(insn)) {
		api-&gt;handler = simulate_cbz_cbnz;
	} else if (aarch64_insn_is_tbz(insn) ||
	    aarch64_insn_is_tbnz(insn)) {
		api-&gt;handler = simulate_tbz_tbnz;
	} else if (aarch64_insn_is_adr_adrp(insn)) {
		api-&gt;handler = simulate_adr_adrp;
	} else if (aarch64_insn_is_b(insn) ||
	    aarch64_insn_is_bl(insn)) {
		api-&gt;handler = simulate_b_bl;
	} else if (aarch64_insn_is_br(insn) ||
	    aarch64_insn_is_blr(insn) ||
	    aarch64_insn_is_ret(insn)) {
		api-&gt;handler = simulate_br_blr_ret;
	} else if (aarch64_insn_is_ldr_lit(insn)) {
		api-&gt;handler = simulate_ldr_literal;
	} else if (aarch64_insn_is_ldrsw_lit(insn)) {
		api-&gt;handler = simulate_ldrsw_literal;
	} else {
		/*
		 * Instruction cannot be stepped out-of-line and we don&#39;t
		 * (yet) simulate it.
		 */
		return INSN_REJECTED;
	}

	return INSN_GOOD_NO_SLOT;
}
```

这里我们可以看到所有白名单指令：

- B 跳转 / B 条件跳转
- CBZ/CBNZ/TBZ/TBNZ
- BL/BR/RET
- ADR/ADRP/LDR/LDRSW

## 总结

使用 uprobes 时，只需要尽量在上述白名单指令位置添加 uprobe 就不会引入 maps 中的特征。

[eDBG](https://github.com/ShinoLeah/eDBG) 提供了完备的内存读取功能，只需要找到离你想要的目标位置最近的一个跳转指令，即可做到无痕地读取目标程序的上下文。


---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/28348c4/  

