# WMCTF2022-Archgame


# [Reverse] Archgame

`load_code`处对bin文件进行了一个解密

```c
for ( i = 0LL; i < size; ++i ) {
 	g_code_data[i] ^= *((_BYTE *)&global_key + (i & 3));
}
```

round()函数有两个switch，手动修复一下，大概逻辑是这个样子。

是一些关于unicorn虚拟机的操作，查一下unicorn引擎的文档可以得到函数作用。

```c
__int64 round()
{
  const char *v0; // rax
  const char *v1; // rax
  const char *v2; // rax
  int errorcode2; // eax
  unsigned int roundkey; // [rsp+0h] [rbp-30h] BYREF
  unsigned int errorcode1; // [rsp+4h] [rbp-2Ch]
  __int64 uc_engine; // [rsp+8h] [rbp-28h] BYREF
  char v8; // [rsp+10h] [rbp-20h] BYREF
  __int64 v9; // [rsp+18h] [rbp-18h] BYREF
  __int64 v10[2]; // [rsp+20h] [rbp-10h] BYREF

  v10[1] = __readfsqword(0x28u);
  errorcode1 = uc_open((unsigned int)g_arch, (unsigned int)g_mode, &uc_engine);
  //创建虚拟机实例
  /* Error Handler */
  errorcode1 = uc_mem_map(uc_engine, 0LL, 655360LL, 7LL);
  //创建从地址0开始 长度655360的内存，权限为RWX
  /* Error Handler */
  uc_mem_write(uc_engine, 0LL, g_code_data, 655360LL);
  //向内存地址0处写入bin文件解密结果
  errorcode1 = uc_mem_map(uc_engine, 0x70000000LL, 0x4000LL, 7LL);
  //创建从地址0x70000000开始 长度0x4000的内存，权限为RWX
  /* Error Handler */
  uc_mem_write(uc_engine, 0x70000000LL, input_area, 0x4000LL);
  //向地址0x70000000写入输入的数据，长度为0x4000
  errorcode2 = uc_mem_map(uc_engine, 0x20000000LL, 0x8000LL, 7LL);
  //创建从地址0x20000000开始 长度0x8000的内存，权限为RWX
  v9 = 536903424LL;
  v10[0] = 1879048448LL;
  switch ( g_arch )
  {
    case 1: //ARM
      uc_reg_write(uc_engine, 12LL, &v9);
      uc_reg_write(uc_engine, 10LL, v10);
      //写寄存器
      break;
    case 2: // ARM-64
      uc_reg_write(uc_engine, 4LL, &v9);
      uc_reg_write(uc_engine, 2LL, v10);
      break;
    case 3: // Mips
      uc_reg_write(uc_engine, 31LL, &v9);
      uc_reg_write(uc_engine, 33LL, v10);
      break;
    case 5: // PowerPC
      uc_reg_write(uc_engine, 3LL, &v9);
      uc_reg_write(uc_engine, 74LL, v10);
      break; 
    case 8: // RISCV
      uc_reg_write(uc_engine, 3LL, &v9);
      uc_reg_write(uc_engine, 2LL, v10);
      break;
  }
  uc_hook_add(uc_engine, (unsigned int)&v8, 1008, (unsigned int)hook_mem, 0, 1, 0LL);
  //hook了一些非法操作，看起来像是异常处理 hook_mem 是nop函数
  errorcode1 = uc_emu_start(uc_engine, 0LL, v9, 0LL, 0LL);
  //从地址0执行到536903424
  switch ( g_arch )
  {
    case 1u:
      uc_reg_read(uc_engine, 66, (__int64)&roundkey);
      //读寄存器
      break;
    case 2u:
      uc_reg_read(uc_engine, 199, (__int64)&roundkey);
      break;
    case 3u:
      uc_reg_read(uc_engine, 4, (__int64)&roundkey);
      break;
    case 5u:
      uc_reg_read(uc_engine, 5, (__int64)&roundkey);
      break;
    case 8u:
      uc_reg_read(uc_engine, 11, (__int64)&roundkey);
      break;
    default:
      break;
  }
  uc_close(uc_engine);
  return roundkey;
}
```

程序的逻辑整体是把challs.bin解密之后加载进来，和输入的fake_flag一起加载到虚拟机中，当flag正确时会返回一个正确的round_key。

global_key 是 round_key 的异或和。每轮使用 round_key 在 map 里寻找对应的 code_info，最后所有 round_key 按顺序拼起来就是 flag。

比较关心的是 g_arch 和 g_mode。查一下unicorn.h的结构体的定义。

```c
typedef enum uc_arch {
    UC_ARCH_ARM = 1, // ARM architecture (including Thumb, Thumb-2)
    UC_ARCH_ARM64,   // ARM-64, also called AArch64
    UC_ARCH_MIPS,    // Mips architecture
    UC_ARCH_X86,     // X86 architecture (including x86 & x86-64)
    UC_ARCH_PPC,     // PowerPC architecture
    UC_ARCH_SPARC,   // Sparc architecture
    UC_ARCH_M68K,    // M68K architecture
    UC_ARCH_RISCV,   // RISCV architecture
    UC_ARCH_S390X,   // S390X architecture
    UC_ARCH_TRICORE, // TriCore architecture
    UC_ARCH_MAX,
} uc_arch;

// Mode type
typedef enum uc_mode {
    UC_MODE_LITTLE_ENDIAN = 0,    // little-endian mode (default mode)
    UC_MODE_BIG_ENDIAN = 1 << 30, // big-endian mode

    // arm / arm64
    UC_MODE_ARM = 0,        // ARM mode
    UC_MODE_THUMB = 1 << 4, // THUMB mode (including Thumb-2)
    // Depreciated, use UC_ARM_CPU_* with uc_ctl instead.
    UC_MODE_MCLASS = 1 << 5, // ARM's Cortex-M series.
    UC_MODE_V8 = 1 << 6,     // ARMv8 A32 encodings for ARM
    UC_MODE_ARMBE8 = 1 << 10, // Big-endian data and Little-endian code.
                              // Legacy support for UC1 only.

    // arm (32bit) cpu types
    // Depreciated, use UC_ARM_CPU_* with uc_ctl instead.
    UC_MODE_ARM926 = 1 << 7,  // ARM926 CPU type
    UC_MODE_ARM946 = 1 << 8,  // ARM946 CPU type
    UC_MODE_ARM1176 = 1 << 9, // ARM1176 CPU type

    // mips
    UC_MODE_MICRO = 1 << 4,    // MicroMips mode (currently unsupported)
    UC_MODE_MIPS3 = 1 << 5,    // Mips III ISA (currently unsupported)
    UC_MODE_MIPS32R6 = 1 << 6, // Mips32r6 ISA (currently unsupported)
    UC_MODE_MIPS32 = 1 << 2,   // Mips32 ISA
    UC_MODE_MIPS64 = 1 << 3,   // Mips64 ISA

    // x86 / x64
    UC_MODE_16 = 1 << 1, // 16-bit mode
    UC_MODE_32 = 1 << 2, // 32-bit mode
    UC_MODE_64 = 1 << 3, // 64-bit mode

    // ppc
    UC_MODE_PPC32 = 1 << 2, // 32-bit mode
    UC_MODE_PPC64 = 1 << 3, // 64-bit mode (currently unsupported)
    UC_MODE_QPX =
        1 << 4, // Quad Processing eXtensions mode (currently unsupported)

    // sparc
    UC_MODE_SPARC32 = 1 << 2, // 32-bit mode
    UC_MODE_SPARC64 = 1 << 3, // 64-bit mode
    UC_MODE_V9 = 1 << 4,      // SparcV9 mode (currently unsupported)

    // riscv
    UC_MODE_RISCV32 = 1 << 2, // 32-bit mode
    UC_MODE_RISCV64 = 1 << 3, // 64-bit mode

    // m68k
} uc_mode;
```

所有的code_info信息在init()函数里可以查到。

```c
v87 = 1995092961;
  v0 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v0 = 12;
  v0[1] = 1;
  v0[2] = 0;
  v0[3] = 1995092961;
  v87 = -1338879771;
  v1 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v1 = 49;
  v1[1] = 5;
  v1[2] = 1073741828;
  v1[3] = -1338879771;
  v87 = 955664102;
  v2 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v2 = 7;
  v2[1] = 1;
  v2[2] = 0;
  v2[3] = 955664102;
  v87 = -1193776029;
  v3 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v3 = 33;
  v3[1] = 2;
  v3[2] = 0;
  v3[3] = -1193776029;
  v87 = 1556007940;
  v4 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v4 = 36;
  v4[1] = 2;
  v4[2] = 0;
  v4[3] = 1556007940;
  v87 = 1847322222;
  v5 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v5 = 6;
  v5[1] = 3;
  v5[2] = 4;
  v5[3] = 1847322222;
  v87 = 614303076;
  v6 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v6 = 37;
  v6[1] = 1;
  v6[2] = 16;
  v6[3] = 614303076;
  v87 = -37846909;
  v7 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v7 = 25;
  v7[1] = 1;
  v7[2] = 16;
  v7[3] = -37846909;
  v87 = -1583722938;
  v8 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v8 = 21;
  v8[1] = 1;
  v8[2] = 16;
  v8[3] = -1583722938;
  v87 = -1442824096;
  v9 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v9 = 2;
  v9[1] = 5;
  v9[2] = 1073741828;
  v9[3] = -1442824096;
  v87 = -1561908451;
  v10 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v10 = 39;
  v10[1] = 1;
  v10[2] = 0x40000000;
  v10[3] = -1561908451;
  v87 = 1591704463;
  v11 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v11 = 40;
  v11[1] = 5;
  v11[2] = 1073741828;
  v11[3] = 1591704463;
  v87 = 469378920;
  v12 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v12 = 17;
  v12[1] = 1;
  v12[2] = 16;
  v12[3] = 469378920;
  v87 = -553294751;
  v13 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v13 = 28;
  v13[1] = 1;
  v13[2] = 16;
  v13[3] = -553294751;
  v87 = 1027702615;
  v14 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v14 = 23;
  v14[1] = 1;
  v14[2] = 0;
  v14[3] = 1027702615;
  v87 = -1842772356;
  v15 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v15 = 47;
  v15[1] = 1;
  v15[2] = 16;
  v15[3] = -1842772356;
  v87 = 765059495;
  v16 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v16 = 18;
  v16[1] = 3;
  v16[2] = 4;
  v16[3] = 765059495;
  v87 = -528682580;
  v17 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v17 = 9;
  v17[1] = 1;
  v17[2] = 0x40000000;
  v17[3] = -528682580;
  v87 = -390187777;
  v18 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v18 = 15;
  v18[1] = 8;
  v18[2] = 4;
  v18[3] = -390187777;
  v87 = -320094565;
  v19 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v19 = 46;
  v19[1] = 1;
  v19[2] = 16;
  v19[3] = -320094565;
  v87 = -132233805;
  v20 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v20 = 26;
  v20[1] = 2;
  v20[2] = 0;
  v20[3] = -132233805;
  v87 = -367134252;
  v21 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v21 = 16;
  v21[1] = 3;
  v21[2] = 4;
  v21[3] = -367134252;
  v87 = 1020344905;
  v22 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v22 = 8;
  v22[1] = 1;
  v22[2] = 16;
  v22[3] = 1020344905;
  v87 = 1537525975;
  v23 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v23 = 42;
  v23[1] = 1;
  v23[2] = 0x40000000;
  v23[3] = 1537525975;
  v87 = 1708482435;
  v24 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v24 = 19;
  v24[1] = 1;
  v24[2] = 0x40000000;
  v24[3] = 1708482435;
  v87 = -1669470713;
  v25 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v25 = 38;
  v25[1] = 1;
  v25[2] = 0x40000000;
  v25[3] = -1669470713;
  v87 = -814646530;
  v26 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v26 = 11;
  v26[1] = 8;
  v26[2] = 4;
  v26[3] = -814646530;
  v87 = 424934441;
  v27 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v27 = 34;
  v27[1] = 1;
  v27[2] = 0x40000000;
  v27[3] = 424934441;
  v87 = -1559295248;
  v28 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v28 = 31;
  v28[1] = 2;
  v28[2] = 0;
  v28[3] = -1559295248;
  v87 = -2121017217;
  v29 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v29 = 12;
  v29[1] = 1;
  v29[2] = 0;
  v29[3] = -2121017217;
  v87 = -1443810010;
  v30 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v30 = 30;
  v30[1] = 1;
  v30[2] = 0;
  v30[3] = -1443810010;
  v87 = -2275378;
  v31 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v31 = 12;
  v31[1] = 1;
  v31[2] = 0;
  v31[3] = -2275378;
  v87 = -249420863;
  v32 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v32 = 33;
  v32[1] = 2;
  v32[2] = 0;
  v32[3] = -249420863;
  v87 = -1480703388;
  v33 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v33 = 0;
  v33[1] = 1;
  v33[2] = 16;
  v33[3] = -1480703388;
  v87 = -100129045;
  v34 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v34 = 33;
  v34[1] = 2;
  v34[2] = 0;
  v34[3] = -100129045;
  v87 = -1216305091;
  v35 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v35 = 7;
  v35[1] = 1;
  v35[2] = 0;
  v35[3] = -1216305091;
  v87 = -1857654124;
  v36 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v36 = 21;
  v36[1] = 1;
  v36[2] = 16;
  v36[3] = -1857654124;
  v87 = -1860618153;
  v37 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v37 = 44;
  v37[1] = 5;
  v37[2] = 1073741828;
  v37[3] = -1860618153;
  v87 = 1535866613;
  v38 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v38 = 33;
  v38[1] = 2;
  v38[2] = 0;
  v38[3] = 1535866613;
  v87 = 814502768;
  v39 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v39 = 21;
  v39[1] = 1;
  v39[2] = 16;
  v39[3] = 814502768;
  v87 = 953980463;
  v40 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v40 = 0;
  v40[1] = 1;
  v40[2] = 16;
  v40[3] = 953980463;
  v87 = 1691496267;
  v41 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v41 = 48;
  v41[1] = 3;
  v41[2] = 4;
  v41[3] = 1691496267;
  v87 = 2126878999;
  v42 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v42 = 0;
  v42[1] = 1;
  v42[2] = 16;
  v42[3] = 2126878999;
  v87 = -1363610825;
  v43 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v43 = 5;
  v43[1] = 2;
  v43[2] = 0;
  v43[3] = -1363610825;
  v87 = 1278447979;
  v44 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v44 = 35;
  v44[1] = 1;
  v44[2] = 16;
  v44[3] = 1278447979;
  v87 = 1274252438;
  v45 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v45 = 43;
  v45[1] = 3;
  v45[2] = 4;
  v45[3] = 1274252438;
  v87 = -63595556;
  v46 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v46 = 25;
  v46[1] = 1;
  v46[2] = 16;
  v46[3] = -63595556;
  v87 = -253633977;
  v47 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v47 = 35;
  v47[1] = 1;
  v47[2] = 16;
  v47[3] = -253633977;
  v87 = 689856462;
  v48 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v48 = 45;
  v48[1] = 1;
  v48[2] = 16;
  v48[3] = 689856462;
  v87 = 1091396509;
  v49 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v49 = 27;
  v49[1] = 1;
  v49[2] = 0x40000000;
  v49[3] = 1091396509;
  v87 = -1260525800;
  v50 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v50 = 23;
  v50[1] = 1;
  v50[2] = 0;
  v50[3] = -1260525800;
  v87 = -1843674714;
  v51 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v51 = 13;
  v51[1] = 2;
  v51[2] = 0;
  v51[3] = -1843674714;
  v87 = -1311132894;
  v52 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v52 = 2;
  v52[1] = 5;
  v52[2] = 1073741828;
  v52[3] = -1311132894;
  v87 = -1771260195;
  v53 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v53 = 4;
  v53[1] = 1;
  v53[2] = 0;
  v53[3] = -1771260195;
  v87 = -1591462304;
  v54 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v54 = 25;
  v54[1] = 1;
  v54[2] = 16;
  v54[3] = -1591462304;
  v87 = -637802572;
  v55 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v55 = 21;
  v55[1] = 1;
  v55[2] = 16;
  v55[3] = -637802572;
  v87 = 1802284995;
  v56 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v56 = 23;
  v56[1] = 1;
  v56[2] = 0;
  v56[3] = 1802284995;
  v87 = 1144704468;
  v57 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v57 = 24;
  v57[1] = 1;
  v57[2] = 0;
  v57[3] = 1144704468;
  v87 = -733124120;
  v58 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v58 = 17;
  v58[1] = 1;
  v58[2] = 16;
  v58[3] = -733124120;
  v87 = -1903496947;
  v59 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v59 = 35;
  v59[1] = 1;
  v59[2] = 16;
  v59[3] = -1903496947;
  v87 = 1538510826;
  v60 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v60 = 16;
  v60[1] = 3;
  v60[2] = 4;
  v60[3] = 1538510826;
  v87 = -1092696830;
  v61 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v61 = 45;
  v61[1] = 1;
  v61[2] = 16;
  v61[3] = -1092696830;
  v87 = -1777550281;
  v62 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v62 = 15;
  v62[1] = 8;
  v62[2] = 4;
  v62[3] = -1777550281;
  v87 = -736103840;
  v63 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v63 = 45;
  v63[1] = 1;
  v63[2] = 16;
  v63[3] = -736103840;
  v87 = 737553787;
  v64 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v64 = 24;
  v64[1] = 1;
  v64[2] = 0;
  v64[3] = 737553787;
  v87 = -1148771148;
  v65 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v65 = 29;
  v65[1] = 1;
  v65[2] = 0;
  v65[3] = -1148771148;
  v87 = -579215339;
  v66 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v66 = 24;
  v66[1] = 1;
  v66[2] = 0;
  v66[3] = -579215339;
  v87 = -756277188;
  v67 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v67 = 15;
  v67[1] = 8;
  v67[2] = 4;
  v67[3] = -756277188;
  v87 = 327766936;
  v68 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v68 = 32;
  v68[1] = 1;
  v68[2] = 0x40000000;
  v68[3] = 327766936;
  v87 = 1424790213;
  v69 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v69 = 27;
  v69[1] = 1;
  v69[2] = 0x40000000;
  v69[3] = 1424790213;
  v87 = 1018490345;
  v70 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v70 = 22;
  v70[1] = 2;
  v70[2] = 0;
  v70[3] = 1018490345;
  v87 = -1247159040;
  v71 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v71 = 43;
  v71[1] = 3;
  v71[2] = 4;
  v71[3] = -1247159040;
  v87 = -971877148;
  v72 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v72 = 27;
  v72[1] = 1;
  v72[2] = 0x40000000;
  v72[3] = -971877148;
  v87 = 1937664642;
  v73 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v73 = 29;
  v73[1] = 1;
  v73[2] = 0;
  v73[3] = 1937664642;
  v87 = 1649910950;
  v74 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v74 = 1;
  v74[1] = 1;
  v74[2] = 0x40000000;
  v74[3] = 1649910950;
  v87 = -700260149;
  v75 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v75 = 20;
  v75[1] = 2;
  v75[2] = 0;
  v75[3] = -700260149;
  v87 = 1138713025;
  v76 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v76 = 38;
  v76[1] = 1;
  v76[2] = 0x40000000;
  v76[3] = 1138713025;
  v87 = 1803201450;
  v77 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v77 = 42;
  v77[1] = 1;
  v77[2] = 0x40000000;
  v77[3] = 1803201450;
  v87 = 1275972721;
  v78 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v78 = 10;
  v78[1] = 8;
  v78[2] = 4;
  v78[3] = 1275972721;
  v87 = 1796321516;
  v79 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v79 = 42;
  v79[1] = 1;
  v79[2] = 0x40000000;
  v79[3] = 1796321516;
  v87 = 1041770612;
  v80 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v80 = 3;
  v80[1] = 5;
  v80[2] = 1073741828;
  v80[3] = 1041770612;
  v87 = 1387353735;
  v81 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v81 = 32;
  v81[1] = 1;
  v81[2] = 0x40000000;
  v81[3] = 1387353735;
  v87 = -2080841071;
  v82 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v82 = 41;
  v82[1] = 8;
  v82[2] = 4;
  v82[3] = -2080841071;
  v87 = 1973486486;
  v83 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v83 = 32;
  v83[1] = 1;
  v83[2] = 0x40000000;
  v83[3] = 1973486486;
  v87 = -829803091;
  v84 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v84 = 34;
  v84[1] = 1;
  v84[2] = 0x40000000;
  v84[3] = -829803091;
  v87 = 0;
  v85 = (_DWORD *)std::map<unsigned int,code_info>::operator[](&g_code_info, &v87);
  *v85 = 14;
  v85[1] = 2;
  v85[2] = 0;
  v85[3] = 0;
```

大概梳理一下 code_info 的存储方式

```c
*v84 = 34; //chall 编号
v84[1] = 1; //g_arch
v84[2] = 0x40000000; //g_mode
v84[3] = -829803091; //round_key
```

程序启动时 round_key 是 0，找到对应文件是 `chall14.bin`，架构是 ARM64，载入之后大概长这个样子：

```c
__int64 sub_0()
{
  int v0; // w8
  int v1; // w9
  char v2; // w9
  char v3; // w8
  char v5; // [xsp+10h] [xbp-260h]
  char v6; // [xsp+14h] [xbp-25Ch]
  __int64 v7; // [xsp+30h] [xbp-240h] BYREF
  int v8; // [xsp+3Ch] [xbp-234h] BYREF
  __int64 *v9; // [xsp+A0h] [xbp-1D0h]
  __int64 *v10; // [xsp+A8h] [xbp-1C8h]
  __int64 **v11; // [xsp+B0h] [xbp-1C0h] BYREF
  __int64 *v12; // [xsp+B8h] [xbp-1B8h] BYREF
  __int64 v13[2]; // [xsp+C0h] [xbp-1B0h] BYREF
  __int64 *v14; // [xsp+D0h] [xbp-1A0h] BYREF
  __int64 v15; // [xsp+D8h] [xbp-198h] BYREF
  __int64 v16[2]; // [xsp+E0h] [xbp-190h] BYREF
  __int64 v17[2]; // [xsp+F0h] [xbp-180h] BYREF
  __int64 v18[11]; // [xsp+100h] [xbp-170h] BYREF
  __int64 v19[2]; // [xsp+158h] [xbp-118h] BYREF
  __int64 v20[2]; // [xsp+168h] [xbp-108h] BYREF
  __int64 v21[2]; // [xsp+178h] [xbp-F8h] BYREF
  __int64 v22[2]; // [xsp+188h] [xbp-E8h] BYREF
  __int64 v23[2]; // [xsp+198h] [xbp-D8h] BYREF
  __int64 *v24; // [xsp+1A8h] [xbp-C8h] BYREF
  __int64 v25[2]; // [xsp+1B0h] [xbp-C0h] BYREF
  __int64 *v26; // [xsp+1C0h] [xbp-B0h] BYREF
  __int64 v27[2]; // [xsp+1C8h] [xbp-A8h] BYREF
  __int64 *v28; // [xsp+1D8h] [xbp-98h] BYREF
  __int64 v29[2]; // [xsp+1E0h] [xbp-90h] BYREF
  __int64 *v30; // [xsp+1F0h] [xbp-80h] BYREF
  __int64 v31[3]; // [xsp+1F8h] [xbp-78h] BYREF
  __int64 v32[2]; // [xsp+210h] [xbp-60h] BYREF
  __int64 *v33; // [xsp+220h] [xbp-50h] BYREF
  __int64 v34[2]; // [xsp+228h] [xbp-48h] BYREF
  __int64 v35[3]; // [xsp+238h] [xbp-38h] BYREF
  __int64 **v36; // [xsp+250h] [xbp-20h] BYREF
  __int64 *v37; // [xsp+258h] [xbp-18h] BYREF

  v7 = 1879048192i64;
  v37 = &v7;
  v36 = &v37;
  v35[2] = (__int64)&v36;
  v35[1] = 1879048192i64;
  if ( MEMORY[0x70000000] == 102 )
  {
    if ( *(_BYTE *)(v7 + 1) == 108 )
    {
      if ( *(_BYTE *)(v7 + 2) == 97 )
      {
        v18[1] = v7 + 3;
        if ( *(_BYTE *)(v7 + 3) == 103 )
        {
          v18[0] = (__int64)&v7;
          v17[1] = (__int64)v18;
          v34[0] = (__int64)&v7;
          v33 = v34;
          v32[1] = (__int64)&v33;
          if ( *(_BYTE *)(v7 + 4) == 123 )
          {
            v0 = *(unsigned __int8 *)(v7 + 5);
            v32[0] = v7 + 6;
            v31[2] = (__int64)v32;
            if ( v0 + *(unsigned __int8 *)(v7 + 6) == 220 )
            {
              return 1995092961;
            }
            else
            {
              v31[1] = v7 + 6;
              v6 = *(_BYTE *)(v7 + 6);
              v31[0] = (__int64)v16;
              v30 = v31;
              v29[1] = (__int64)&v30;
              v16[0] = (__int64)&v7;
              v29[0] = (__int64)&v7;
              v28 = v29;
              v27[1] = (__int64)&v28;
              if ( (unsigned __int8)(v6 - *(_BYTE *)(v7 + 7)) == 179 )
              {
                return (unsigned int)-1693198170;
              }
              else
              {
                v27[0] = (__int64)&v15;
                v26 = v27;
                v25[1] = (__int64)&v26;
                v15 = v7 + 7;
                v14 = &v15;
                v13[1] = (__int64)&v14;
                v25[0] = (__int64)&v14;
                v24 = v25;
                v23[1] = (__int64)&v24;
                v5 = *(_BYTE *)(v7 + 7);
                v13[0] = (__int64)&v7;
                v12 = v13;
                v23[0] = (__int64)&v11;
                v22[1] = (__int64)v23;
                v11 = &v12;
                v22[0] = (__int64)v13;
                v21[1] = (__int64)v22;
                v1 = *(unsigned __int8 *)(v7 + 8);
                if ( (((v5 & 2 | ((~v5 & 0xF8 | v5 & 7) ^ 7) & 0x80) ^ 0x80 | (v5 & 4 | ((~v5 & 0xF8 | v5 & 7) ^ 7) & 1) ^ 4 | v5 & 0x78) ^ ((v1 & 2 | ~(_BYTE)v1 & 0x80) ^ 0x80 | (~v1 & 4 | v1 & 1) ^ 1 | v1 & 0x78)) == 81 )
                {
                  return (unsigned int)-512132426;
                }
                else
                {
                  v2 = *(_BYTE *)(v7 + 8);
                  v10 = &v7;
                  if ( (unsigned __int8)(*(_BYTE *)(v7 + 9) + v2) == 47 )
                  {
                    return (unsigned int)-1338879771;
                  }
                  else
                  {
                    v3 = *(_BYTE *)(v7 + 9);
                    v21[0] = (__int64)&v7;
                    v20[1] = (__int64)v21;
                    v20[0] = v7 + 10;
                    v19[1] = (__int64)v20;
                    if ( (unsigned __int8)(v3 - *(_BYTE *)(v7 + 10)) == 246 )
                    {
                      return (unsigned int)-1203572107;
                    }
                    else
                    {
                      v9 = &v7;
                      if ( (unsigned __int8)(*(_BYTE *)(v7 + 10) + *(_BYTE *)(v7 + 11)) == 124 )
                      {
                        v19[0] = (__int64)&v8;
                        v18[10] = (__int64)v19;
                        return 955664102;
                      }
                      else
                      {
                        return 1428707764;
                      }
                    }
                  }
                }
              }
            }
          }
          else
          {
            v17[0] = (__int64)&v8;
            v16[1] = (__int64)v17;
            return 1428707764;
          }
        }
        else
        {
          return 1428707764;
        }
      }
      else
      {
        v18[2] = (__int64)&v8;
        return 1428707764;
      }
    }
    else
    {
      v18[3] = (__int64)&v8;
      return 1428707764;
    }
  }
  else
  {
    v35[0] = (__int64)&v8;
    v34[1] = (__int64)v35;
    return 1428707764;
  }
}
```

观察到程序的返回值只有几种，而程序判断 fake_flag 是否正确的逻辑是在 map 里寻找有没有对应的 key。考虑无视程序逻辑，直接在 init 程序中遍历搜索这几种返回值直到找到一个存在的round_key。

虽然有多个返回值可以搜到，但由于challs是用前面所有round_key的异或和解密，可以认为如果按照对应架构载入能被IDA正确解析则key正确，否则key错误。

```python
from Crypto.Util.number import *
global_key = 0
round_key = [1995092961, 0xB8D86C63, 1556007940, 614303076, 0xFDBE8083, 0xAA004060, 1591704463, 469378920, 0x9229867C, 0xE07CF1AC, 0xF81E45B3, 1020344905, 1708482435, 424934441, 3076655192]
key = [0, 0, 0, 0]
for what in round_key:
	global_key ^= what
bts = long_to_bytes(global_key)
print(bts[0])
key[3] = bts[0]
key[2] = bts[1]
key[1] = bts[2]
key[0] = bts[3]
index_table = [14, 12, 33, 36, 37, 25, 2, 40, 17, 47, 9, 26, 8, 19, 34]
index = 34
f = open(f"challs/chall{index}.bin", "rb")
byte = f.read()
res = b""
for i in range(len(byte)):
	print(long_to_bytes(byte[i] ^ key[i&3]))
	res += long_to_bytes(byte[i] ^ key[i&3])
otp = open(f"challs_solved/chall{index}.bin", "wb")
otp.write(res)
```

这样找到的 round 顺序最终为`[14, 12, 33, 36, 37, 25, 2, 40, 17, 47, 9, 26, 8, 19, 34]`

将round_key拼接得到flag。

`wmctf{76eab3e1b8d86c635cbecc04249d8564fdbe8083aa0040605edf7b8f1bfa27689229867ce07cf1acf81e45b33cd13a4965d55f831953fc29b7620858}`


