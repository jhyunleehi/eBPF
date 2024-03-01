# Lab

## 1. Build opensnoop 

```
$ cd  cd  bcc/libbpf-tools
$ make opensnoop
$ ./opensnoop
```

## 2. Ojbect file 

#### readelf 
* BPF 프로그램이 실제 어떻게 적재될지 정의  
```
# readelf --section-details --headers .output/opensnoop.bpf.o -W
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           Linux BPF   <<<-----------------Linux BPF machine 
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          11960 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         20
  Section header string table index: 1

Section Headers:
  [Nr] Name
       Type            Address          Off    Size   ES   Lk Inf Al Flags
  [ 0] NULL            0000000000000000 000000 000000 00   0   0  0  [0000000000000000]: 
  [ 1] .strtab
       STRTAB          0000000000000000 002c93 000224 00   0   0  1  [0000000000000000]: 
  [ 2] .text
       PROGBITS        0000000000000000 000040 000000 00   0   0  4  [0000000000000006]: ALLOC, EXEC
  [ 3] tracepoint/syscalls/sys_enter_open  <<<<-------------trace point #1
       PROGBITS        0000000000000000 000040 000170 00   0   0  8  [0000000000000006]: ALLOC, EXEC
  [ 4] .reltracepoint/syscalls/sys_enter_open
       REL             0000000000000000 0022d8 000040 10  19   3  8  [0000000000000040]: INFO LINK
  [ 5] tracepoint/syscalls/sys_enter_openat  <<<<-------------trace point #2 
       PROGBITS        0000000000000000 0001b0 000170 00   0   0  8  [0000000000000006]: ALLOC, EXEC
  [ 6] .reltracepoint/syscalls/sys_enter_openat
       REL             0000000000000000 002318 000040 10  19   5  8  [0000000000000040]: INFO LINK
  [ 7] tracepoint/syscalls/sys_exit_open    <<<<-------------trace point #3 
       PROGBITS        0000000000000000 000320 000330 00   0   0  8  [0000000000000006]: ALLOC, EXEC
  [ 8] .reltracepoint/syscalls/sys_exit_open
       REL             0000000000000000 002358 000040 10  19   7  8  [0000000000000040]: INFO LINK
  [ 9] tracepoint/syscalls/sys_exit_openat   <<<<-------------trace point #4
       PROGBITS        0000000000000000 000650 000330 00   0   0  8  [0000000000000006]: ALLOC, EXEC
  [10] .reltracepoint/syscalls/sys_exit_openat
       REL             0000000000000000 002398 000040 10  19   9  8  [0000000000000040]: INFO LINK
  [11] .rodata
       PROGBITS        0000000000000000 000980 00000d 00   0   0  4  [0000000000000002]: ALLOC
  [12] .maps
       PROGBITS        0000000000000000 000990 000038 00   0   0  8  [0000000000000003]: WRITE, ALLOC
  [13] license
       PROGBITS        0000000000000000 0009c8 000004 00   0   0  1  [0000000000000003]: WRITE, ALLOC
  [14] .BTF
       PROGBITS        0000000000000000 0009cc 000d8e 00   0   0  4  [0000000000000000]: 
  [15] .rel.BTF
       REL             0000000000000000 0023d8 000070 10  19  14  8  [0000000000000040]: INFO LINK
  [16] .BTF.ext
       PROGBITS        0000000000000000 00175c 0008ac 00   0   0  4  [0000000000000000]: 
  [17] .rel.BTF.ext
       REL             0000000000000000 002448 000840 10  19  16  8  [0000000000000040]: INFO LINK
  [18] .llvm_addrsig
       LOOS+0xfff4c03  0000000000000000 002c88 00000b 00   0   0  1  [0000000080000000]: EXCLUDE
  [19] .symtab
       SYMTAB          0000000000000000 002008 0002d0 18   1  19  8  [0000000000000000]: 

```

####  opensnoop.bpf.c 
* 실제 커널에 설치되는 파일  

```c
#define SEC(name) __attribute__((section(name), used))

#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include "opensnoop.h"

const volatile pid_t targ_pid = 0;
const volatile pid_t targ_tgid = 0;
const volatile uid_t targ_uid = 0;
const volatile bool targ_failed = false;

struct {...} start SEC(".maps");
struct {...} events SEC(".maps");
static __always_inline bool valid_uid(uid_t uid) {return uid != INVALID_UID;}

SEC("tracepoint/syscalls/sys_enter_open")
int tracepoint__syscalls__sys_enter_open(struct trace_event_raw_sys_enter* ctx)
{...}

SEC("tracepoint/syscalls/sys_enter_openat")
int tracepoint__syscalls__sys_enter_openat(struct trace_event_raw_sys_enter* ctx)
{...}


SEC("tracepoint/syscalls/sys_exit_open")
int tracepoint__syscalls__sys_exit_open(struct trace_event_raw_sys_exit* ctx)
{...}

SEC("tracepoint/syscalls/sys_exit_openat")
int tracepoint__syscalls__sys_exit_openat(struct trace_event_raw_sys_exit* ctx)
{...}

char LICENSE[] SEC("license") = "GPL";

```

* Each of these is preceded by a SEC() macro which corresponds to the executable sections listed by readelf. 
* It defines the eBPF hook where the code should be attached to (SEC("tracepoint/<category>/<name>")). 
* In our case to the eBPF tracepoints sys_enter_open and sys_enter_openat, as our eBPF code should be called whenever a open and openat syscall is issued ("entered", therefore sys_enter). 
* Tracepoints are static markers in the kernel’s code that you can use to attach (eBPF) code in a running kernel. 
* These tracepoint are often placed in locations which are interesting or common locations to measure performance.

* The tracepoint__syscalls__sys_enter_open and tracepoint__syscalls__sys_enter_openat functions get executed whenever a open()/openat() syscall is issued. 
* They then parse the arguments (filename, etc.) of the call and write this information to the BPF map. 
* From there, our compiled opensnoop.c binary part - our user-space program (USP) - can read and print it to STDOUT.

## bpftool 
*  tool for inspection and simple manipulation of eBPF programs and maps
*  `$ bpftool prog list`
```
NAME
       BPFTOOL - tool for inspection and simple manipulation of eBPF programs and maps

SYNOPSIS
          bpftool [OPTIONS] OBJECT { COMMAND | help }
          bpftool batch file FILE
          bpftool version
          OBJECT := { prog | map | link | cgroup | perf | net | feature | btf | gen | struct_ops | iter }
          OPTIONS := { { -V | --version } | { -j | --json } [{ -p | --pretty }] | { -d | --debug } }
          MAP-COMMANDS := { show | list | create | dump | update | lookup | getnext | delete | pin | event_pipe | help }
          PROG-COMMANDS := { show | list | dump jited | dump xlated | pin | load | attach | detach | help }
          CGROUP-COMMANDS := { show | list | attach | detach | help }
          PERF-COMMANDS := { show | list | help }
          NET-COMMANDS := { show | list | help }
          FEATURE-COMMANDS := { probe | help }
```


#### bpftool prog list

```
# opensnoop 
# bpftool prog list 
159: tracepoint  name tracepoint__syscalls__sys_enter_open  tag 07014be5359438f8  gpl
        loaded_at 2024-02-09T16:37:14+0000  uid 0
        xlated 240B  jited 137B  memlock 4096B  map_ids 31,28  <<------map id 31번 참조
        btf_id 111
        pids opensnoop(2658)
161: tracepoint  name tracepoint__syscalls__sys_enter_openat  tag 8ee3432dcd98ffc3  gpl
        loaded_at 2024-02-09T16:37:14+0000  uid 0
        xlated 240B  jited 137B  memlock 4096B  map_ids 31,28  <<------map id 31번 참조 
        btf_id 111
        pids opensnoop(2658)
162: tracepoint  name tracepoint__syscalls__sys_exit_open  tag 37f628f9e857b071  gpl
        loaded_at 2024-02-09T16:37:14+0000  uid 0
        xlated 792B  jited 546B  memlock 4096B  map_ids 28,31,29   <<------map id
        btf_id 111
        pids opensnoop(2658)
163: tracepoint  name tracepoint__syscalls__sys_exit_openat  tag 37f628f9e857b071  gpl
        loaded_at 2024-02-09T16:37:14+0000  uid 0
        xlated 792B  jited 546B  memlock 4096B  map_ids 28,31,29  <<------map id
        btf_id 111
        pids opensnoop(2658)
```
#### bpftool map list
```
# bpftool map list
28: hash  name start  flags 0x0
        key 4B  value 16B  max_entries 10240  memlock 245760B
        btf_id 111
        pids opensnoop(2658)
29: perf_event_array  name events  flags 0x0
        key 4B  value 4B  max_entries 1  memlock 4096B
        pids opensnoop(2658)
31: array  name opensnoo.rodata  flags 0x480   <<<<<<-----------Map id 31번 
        key 4B  value 13B  max_entries 1  memlock 4096B
        btf_id 111  frozen
        pids opensnoop(2658)
38: array  name libbpf_global  flags 0x0
        key 4B  value 32B  max_entries 1  memlock 4096B
39: array  name pid_iter.rodata  flags 0x480
        key 4B  value 4B  max_entries 1  memlock 4096B
        btf_id 129  frozen
        pids bpftool(2672)
40: array  name libbpf_det_bind  flags 0x0
        key 4B  value 32B  max_entries 1  memlock 4096B
```

####  map 관련 데이터 코드 정의는 여기서
```c
struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__uint(max_entries, 10240);
	__type(key, u32);
	__type(value, struct args_t);
} start SEC(".maps");

struct {
	__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
	__uint(key_size, sizeof(u32));
	__uint(value_size, sizeof(u32));
} events SEC(".maps");

```



#### 159 번 xlated id dump

```log
# bpftool  prog dum xlated id 159 linum
int tracepoint__syscalls__sys_enter_open(struct trace_event_raw_sys_enter * ctx):
; int tracepoint__syscalls__sys_enter_open(struct trace_event_raw_sys_enter* ctx) [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:50 line_col:0]
   0: (bf) r6 = r1
; u64 id = bpf_get_current_pid_tgid(); [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:52 line_col:11]
   1: (85) call bpf_get_current_pid_tgid#213088
; u32 pid = id; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:55 line_col:6]
   2: (63) *(u32 *)(r10 -4) = r0
; if (targ_tgid && targ_tgid != tgid) [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:36 line_col:6]
   3: (18) r1 = map[id:31][0]+4
   5: (61) r2 = *(u32 *)(r1 +0)
; if (targ_pid && targ_pid != pid) [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:38 line_col:6]
   6: (18) r1 = map[id:31][0]+0
   8: (61) r2 = *(u32 *)(r1 +0)
; if (valid_uid(targ_uid)) { [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:40 line_col:16]
   9: (18) r7 = map[id:31][0]+8
  11: (61) r1 = *(u32 *)(r7 +0)
  12: (18) r2 = 0xffffffff
; if (targ_uid != uid) { [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:42 line_col:7]
  14: (b7) r1 = 0
; struct args_t args = {}; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:59 line_col:17]
  15: (7b) *(u64 *)(r10 -16) = r1
; args.fname = (const char *)ctx->args[0]; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:60 line_col:30]
  16: (79) r1 = *(u64 *)(r6 +16)
; args.fname = (const char *)ctx->args[0]; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:60 line_col:14]
  17: (7b) *(u64 *)(r10 -24) = r1
; args.flags = (int)ctx->args[1]; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:61 line_col:21]
  18: (79) r1 = *(u64 *)(r6 +24)
; args.flags = (int)ctx->args[1]; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:61 line_col:14]
  19: (63) *(u32 *)(r10 -16) = r1
  20: (bf) r2 = r10
; struct args_t args = {}; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:59 line_col:17]
  21: (07) r2 += -4
  22: (bf) r3 = r10
  23: (07) r3 += -24
; bpf_map_update_elem(&start, &pid, &args, 0); [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:62 line_col:3]
  24: (18) r1 = map[id:28]
  26: (b7) r4 = 0
  27: (85) call htab_map_update_elem#251088
; return 0; [file:/opt/ebpf/bcc/libbpf-tools/opensnoop.bpf.c line_num:64 line_col:2]
  28: (b7) r0 = 0
  29: (95) exit
  ```