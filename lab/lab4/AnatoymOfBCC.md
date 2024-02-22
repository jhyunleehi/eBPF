# Anatomy of an eBPF Program


eBPF 프로그램은 eBPF 바이트코드 명령어의 집합입니다. 어셈블리어로 프로그래밍하는 것이 가능한 것처럼, eBPF 코드를 직접 이 바이트코드로 작성할 수 있습니다. 보통 인간들은 더 높은 수준의 프로그래밍 언어를 다루기 쉽다고 생각하는데, 적어도 이 글을 쓰는 시점에서는 대다수의 eBPF 코드가 C로 작성되고 그런 다음 eBPF 바이트코드로 컴파일됩니다.

## eBPF 가상 머신 

eBPF 가상 머신은 모든 가상 머신처럼 컴퓨터의 소프트웨어 구현입니다. 이것은 eBPF 바이트코드 명령어 형태의 프로그램을 받아들이고, 이들은 CPU에서 실행되는 기계어로 변환되어야 합니다.


eBPF의 초기 구현에서는 바이트코드 명령어가 커널 내에서 해석되었습니다. 즉, eBPF 프로그램이 실행될 때마다 커널이 명령어를 검사하고 이를 기계 코드로 변환하여 실행합니다. 하지만 성능 문제 및 eBPF 해석기에서 발생할 수 있는 몇 가지 Spectre 관련 취약점을 피하기 위해 JIT (just-in-time) 컴파일로 대부분 대체되었습니다. 컴파일이라 함은 프로그램이 커널에 로드될 때 한 번만 네이티브 기계 명령어로 변환되는 것을 의미합니다.


### eBPF Registers


eBPF 가상 머신은 0부터 9까지 번호가 매겨진 10개의 범용 레지스터를 사용합니다. 
* 상태 레지스터 :  레지스터 10은 스택 프레임 포인터로 사용되며 (읽기 전용이지만 쓰기는 불가능합니다), 상태를 추적하기 위해 실행 중에 이러한 레지스터에 값이 저장됩니다.

이러한 eBPF 레지스터는 소프트웨어로 구현됩니다. Linux 커널 소스 코드의 include/uapi/linux/bpf.h 헤더 파일에서 BPF_REG_0에서 BPF_REG_10까지 열거된 것을 볼 수 있습니다.

* eBPF 프로그램의 실행이 시작되기 전에 컨텍스트 인수는 레지스터 1에 로드됩니다. 
* 함수에서의 반환 값은 레지스터 0에 저장됩니다.

* eBPF 코드에서 함수를 호출하기 전에 해당 함수의 인수는 레지스터 1부터 레지스터 5까지에 배치됩니다 (인수가 다섯 개보다 적으면 모든 레지스터가 사용되지 않습니다).

### eBPF Instructions

The same /usr/incclude/linux/bpf.h header file defines a structure called bpf_insn, which represents a BPF instruction:

```c
/* BPF has 10 general purpose 64-bit registers and stack frame. */
#define MAX_BPF_REG     __MAX_BPF_REG

struct bpf_insn {
        __u8    code;           /* opcode */
        __u8    dst_reg:4;      /* dest register */
        __u8    src_reg:4;      /* source register */
        __s16   off;            /* signed offset */
        __s32   imm;            /* signed immediate constant */
};

/* Register numbers */
enum {
        BPF_REG_0 = 0,
        BPF_REG_1,
        BPF_REG_2,
        BPF_REG_3,
        BPF_REG_4,
        BPF_REG_5,
        BPF_REG_6,
        BPF_REG_7,
        BPF_REG_8,
        BPF_REG_9,
        BPF_REG_10,
        __MAX_BPF_REG,
};

```

op code 유형 
• 레지스터에 값 로드하기 (즉시 값 또는 메모리 또는 다른 레지스터에서 읽은 값)
• 레지스터에서 메모리로 값 저장하기
• 레지스터 내용에 값 추가와 같은 산술 연산 수행
• 특정 조건이 충족되면 다른 명령어로 점프하기

## eBPF “Hello World” for a Network Interface


```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

int counter = 0;

SEC("xdp")
int hello(struct xdp_md *ctx) {
    bpf_printk("Hello World %d", counter);
    counter++; 
    return XDP_PASS;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```
## Compiling an eBPF Object File
* 여기서 중요한 것은  -target을 bpf로 정해서 컴파일 한다는 것이다.  
```c
TARGETS = hello hello-func

all: $(TARGETS)
.PHONY: all

$(TARGETS): %: %.bpf.o 

%.bpf.o: %.bpf.c
	clang  -target bpf \
		-I/usr/include/$(shell uname -m)-linux-gnu \
		-g \
	    -O2 -o $@ -c $<
```        
- Makefile에서 '%' 기호는 패턴 규칙을 나타냅니다.
- "$@" 또는 "$(@)"는 바로 Target 을 말합니다. 
- "$<"는 열거된 Depend중에 가장 왼쪽에 기술된 1개의 Depend를 말하며 "$^"는 Depend 전체를 의미합니다. 이것은 앞으로도 "make"를 사용하는데 있어서 굉장히 많은 부분 기여하는 매크로

- "$?" 로 있는데 이것은 Target과 Depend의 변경날짜를 비교하여 Depend의 변경날짜중에 최근에 변경된것만 선택하는 매크로입니다. "$?"는 주로 라이브러리의 생성 및 관리시에 사용
- 확장자 ".c"를 가진 파일을 확장자 ".o"를 가진 파일로 생성하는 공통적인 확장자 규칙을 예로 작성한 것입니다.

```
%.o: %.c
    gcc -c $< -o $@
```
* 이 규칙은 '.o' 확장자를 가진 모든 파일에 대해 '.c' 확장자를 가진 소스 파일을 컴파일하여 오브젝트 파일을 생성합니다. 여기서 '%' 기호는 임의의 문자열로 대체됩니다.

### eBPF object file


```
$ file hello.bpf.o
hello.bpf.o: ELF 64-bit LSB relocatable, eBPF, version 1 (SYSV), with debug_info, not stripped

$ readelf -l  hello.bpf.o

There are no program headers in this file.
readelf: Warning: unable to apply unsupported reloc type 3 to section .debug_info
$ readelf -h  hello.bpf.o
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           Linux BPF
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          3960 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         27
  Section header string table index: 1
readelf: Warning: unable to apply unsupported reloc type 3 to section .debug_info


$ ldd hello.bpf.o 
        not a dynamic executable

```

### objdump 
```
$ llvm-objdump-14 -S  hello.bpf.o

hello.bpf.o:    file format elf64-bpf

Disassembly of section xdp:

0000000000000000 <hello>:
;     bpf_printk("Hello World %d", counter);
       0:       18 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 r6 = 0 ll
       2:       61 63 00 00 00 00 00 00 r3 = *(u32 *)(r6 + 0)
       3:       18 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 r1 = 0 ll
       5:       b7 02 00 00 0f 00 00 00 r2 = 15
       6:       85 00 00 00 06 00 00 00 call 6
;     counter++; 
       7:       61 61 00 00 00 00 00 00 r1 = *(u32 *)(r6 + 0)
       8:       07 01 00 00 01 00 00 00 r1 += 1
       9:       63 16 00 00 00 00 00 00 *(u32 *)(r6 + 0) = r1
;     return XDP_PASS;
      10:       b7 00 00 00 02 00 00 00 r0 = 2
      11:       95 00 00 00 00 00 00 00 exit
```      


### gdb

```
$ sudo gdb ./hello.bpf.o 
(gdb) p
The history is empty.
(gdb) l
1       #include <linux/bpf.h>
2       #include "bpf/bpf_helpers.h"
3
4       int counter = 0;
5
6       SEC("xdp")
7       int hello(struct xdp_md *ctx) {
8           bpf_printk("Hello World %d", counter);
9           counter++; 
10          return XDP_PASS;
(gdb) b 7
Breakpoint 1 at 0x0: file hello.bpf.c, line 7.

(gdb) i b 
Num     Type           Disp Enb Address    What
1       breakpoint     keep y   0x00000000 in hello at hello.bpf.c:7

(gdb) info file
Symbols from "/home/jhyunlee/code/eBPF/learning-ebpf/chapter3/hello.bpf.o".
Local exec file:
        `/home/jhyunlee/code/eBPF/learning-ebpf/chapter3/hello.bpf.o', file type elf64-little.
        Entry point: 0x0
        0x00000000 - 0x00000000 is .text
        0x00000000 - 0x00000060 is xdp
        0x00000060 - 0x00000064 is .bss
        0x00000064 - 0x00000073 is .rodata
        0x00000073 - 0x00000080 is license
(gdb) info proc
No current process: you must name one.
```



## loading Program into Kernel

* bpfcc-tools 설치를 하면 bpfcc 패키지가 모두 설치되므로... 이것은 설치하지 않는다.  
```
jhyunlee@Good:/usr/share/bcc/tools$ apt list | grep  bcc
bcc/jammy 0.16.17-3.3 amd64
$ sudo apt install bpfcc-tools

```

### bpftool 컴파일 설치   
* /home/jhyunlee/code/eBPF/bcc/libbpf-tools/bpftool


```
hyunlee@Good:~/code$ git clone --recurse-submodules https://github.com/libbpf/bpftool.git
jhyunlee@Good:~/code/bpftool$ git submodule update --init
jhyunlee@Good:~/code/bpftool$ cd src
jhyunlee@Good:~/code/bpftool/src$ make
jhyunlee@Good:~/code/bpftool/src$ export  LANG=C
jhyunlee@Good:~/code/bpftool/src$ make
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  GEN      profiler.skel.h
  CC       prog.o
  CC       struct_ops.o
  CC       tracelog.o
  CC       xlated_dumper.o
  CC       disasm.o
  LINK     bpftool

jhyunlee@Good:~/code/bpftool/src$ sudo make install
[sudo] password for jhyunlee: 
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  INSTALL  bpftool
jhyunlee@Good:~/code/bpftool/src$ bpftool

Usage: bpftool [OPTIONS] OBJECT { COMMAND | help }
       bpftool batch file FILE
       bpftool version

       OBJECT := { prog | map | link | cgroup | perf | net | feature | btf | gen | struct_ops | iter }
       OPTIONS := { {-j|--json} [{-p|--pretty}] | {-d|--debug} |
                    {-V|--version} }

jhyunlee@Good:~/code/bpftool/src$ which bpftool
/usr/local/sbin/bpftool
```



## bpftool 
```
$ sudo bpftool prog load hello.bpf.o  /sys/fs/bpf/hello


$ sudo ls /sys/fs/bpf
hello  snap

$ sudo  bpftool prog list
...
487: xdp  name hello  tag d35b94b4c0c10efb  gpl
        loaded_at 2024-02-22T15:25:04+0900  uid 0
        xlated 96B  jited 67B  memlock 4096B  map_ids 20,21
        btf_id 185
```        
```
$ sudo  bpftool prog show id 487 --pretty
{
    "id": 487,
    "type": "xdp",
    "name": "hello",
    "tag": "d35b94b4c0c10efb",
    "gpl_compatible": true,
    "loaded_at": 1708583104,
    "uid": 0,
    "orphaned": false,
    "bytes_xlated": 96,
    "jited": true,
    "bytes_jited": 67,
    "bytes_memlock": 4096,
    "map_ids": [20,21
    ],
    "btf_id": 185
}
```

### The BPF Program Tag
• bpftool prog show id 540
• bpftool prog show name hello
• bpftool prog show tag d35b94b4c0c10efb
• bpftool prog show pinned /sys/fs/bpf/hello

### Translated Bytecode 

```
$ sudo bpftool prog dump xlated name hello
int hello(struct xdp_md * ctx):
; bpf_printk("Hello World %d", counter);
   0: (18) r6 = map[id:20][0]+0
   2: (61) r3 = *(u32 *)(r6 +0)
   3: (18) r1 = map[id:21][0]+0
   5: (b7) r2 = 15
   6: (85) call bpf_trace_printk#-108416
; counter++; 
   7: (61) r1 = *(u32 *)(r6 +0)
   8: (07) r1 += 1
   9: (63) *(u32 *)(r6 +0) = r1
; return XDP_PASS;
  10: (b7) r0 = 2
  11: (95) exit
```  

### map Global Variables
* eBPF 맵은 eBPF 프로그램이나 사용자 공간에서 액세스할 수 있는 데이터 구조입니다. 
* 동일한 프로그램의 여러 실행에서 동일한 맵에 반복적으로 액세스할 수 있기 때문에 한 실행에서 다음으로 상태를 유지하는 데 사용될 수 있습니다. 
* 여러 프로그램이 동일한 맵에 액세스할 수도 있습니다. 이러한 특성으로 인해 맵의 의미론이 전역 변수로 사용될 수 있습니다.

```
$ sudo  bpftool map list
2: prog_array  name hid_jmp_table  flags 0x0
        key 4B  value 4B  max_entries 1024  memlock 8512B
        owner_prog_type tracing  owner jited
3: hash  flags 0x0
        key 9B  value 1B  max_entries 500  memlock 46816B
4: hash  flags 0x0
        key 9B  value 1B  max_entries 500  memlock 46816B
5: hash  flags 0x0
        key 9B  value 1B  max_entries 500  memlock 46816B
6: hash  flags 0x0
        key 9B  value 1B  max_entries 500  memlock 46816B
12: perf_event_array  name events  flags 0x0
        key 4B  value 4B  max_entries 16  memlock 448B
        pids python(123587)
20: array  name hello.bss  flags 0x400
        key 4B  value 4B  max_entries 1  memlock 8192B
        btf_id 185
21: array  name hello.rodata  flags 0x80
        key 4B  value 15B  max_entries 1  memlock 336B
        btf_id 185  frozen
36: array  name libbpf_global  flags 0x0
        key 4B  value 32B  max_entries 1  memlock 352B
37: array  name pid_iter.rodata  flags 0x480
        key 4B  value 4B  max_entries 1  memlock 8192B
        btf_id 225  frozen
        pids bpftool(159240)
38: array  name libbpf_det_bind  flags 0x0
```


```
$ sudo  bpftool map dump name hello.rodata
[{
        "value": {
            ".rodata": [{
                    "hello.____fmt": "Hello World %d"
                }
            ]
        }
    }
]
```

### unloading bpf program  

```
$ sudo ls /sys/fs/bpf/hello
/sys/fs/bpf/hello

$ sudo rm  /sys/fs/bpf/hello
$ sudo bpftool prog show name hello
```
