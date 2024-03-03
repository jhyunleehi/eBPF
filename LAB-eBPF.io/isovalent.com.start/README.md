# Lab

## 1. Build opensnoop 

```
$ cd  cd  bcc/libbpf-tools
$ make opensnoop
$ ./opensnoop
```
사용자 공간 프로그램(USP)은 커널 공간 프로그램을 선언하고 해당 추적점/프로브에 연결합니다.
커널 공간 프로그램(KSP)은 추적점/프로브를 만나면 트리거되고 커널 내에서 실행됩니다. 여기에 실제 eBPF 로직이 구현됩니다.
이 두 프로그램은 서로 직접 통신할 수 없으므로(설계상), 데이터를 교환하기 위해 버퍼가 필요합니다. eBPF의 경우 다양한 유형의 BPF 맵을 통해 구현됩니다.

opensnoop 이라는 컴파일된 이진 파일을 실행하려면 CAP_BPF Linux 능력이 필요합니다. 이는 우리의 논리가 특권 있는 BPF 작업(예: eBPF 코드를 커널에 로드)을 사용하기 때문에 필수적이며 동시에 많은 Linux 배포판에서 특권 없는 eBPF를 허용하지 않기 때문입니다. CAP_BPF 능력은 Linux 커널 5.8 이후부터 사용 가능하며 모든 유형의 BPF 프로그램을 로드하고 대부분의 맵 유형을 생성하며 BTF를 로드하고 프로그램과 맵을 반복하는 등의 작업을 허용합니다. CAP_SYS_ADMIN 능력이 과부화되어 있는 BPF 기능을 분리하기 위해 도입되었습니다.

그러나 이 데모 환경에서는 이미 루트로 실행 중이기 때문에 이는 문제가 되지 않습니다. opensnoop를 실행하세요.

## 2. Ojbect file 

객체 파일은 ELF 형식입니다. ELF는 "실행 가능 및 링크 가능 형식"을 나타내며 실행 파일, 오브젝트 코드, 공유 라이브러리 및 코어 덤프에 대한 공통 표준 파일 형식을 나타냅니다. 또한 x86 프로세서의 이진 파일에 대한 표준 파일 형식입니다.

주목할 몇 가지 흥미로운 점:

머신은 Linux BPF입니다. 따라서 이 바이너리 코드는 BPF 인커널 가상 머신 내에서 실행될 목적입니다.
이 파일에는 BTF 정보가 포함되어 있습니다. BTF는 BPF 프로그램/맵에 관련된 디버그 정보를 인코딩하는 메타데이터 형식입니다. 이 디버그 정보는 맵 프리티 프린트, 함수 시그니처 등에 사용됩니다.
테이블에서 .text라는 섹션 헤더 뒤에는 tracepoint로 시작하는 네 개의 실행 가능한 섹션이 있습니다. 이것들은 네 개의 BPF 프로그램에 해당합니다.
BPF 소스 코드에서 이 네 가지 프로그램을 찾아 봅시다. 두 번째 탭인 </> Editor에서 opensnoop.bpf.c 파일을 열어보세요 - 우리의 커널 스페이스 프로그램 (KSP). 50, 68, 125 및 131번째 줄에서 시작하는 int tracepoint__syscalls....라는 이름의 네 가지 다른 함수를 찾을 수 있어야 합니다.

각각은 readelf에 나열된 실행 가능한 섹션에 해당하는 SEC() 매크로로 시작합니다. 
* 코드가 첨부될 eBPF 후크를 정의합니다 (SEC("tracepoint/<category>/<name>")). 
* 우리의 경우 open 및 openat 시스템 호출이 발생할 때마다 이 코드가 호출되어야 하므로 ("entered", 따라서 sys_enter). 
* Tracepoint는 커널의 코드에서 정적 표식으로 커널의 실행 중에 (eBPF) 코드를 첨부할 수 있는 위치에 배치됩니다. 

이러한 tracepoint는 성능을 측정하는 데 흥미로운 위치 또는 일반적인 위치에 자주 배치됩니다.
* tracepoint__syscalls__sys_enter_open tracepoint__syscalls__sys_enter_openat 함수는 open()/openat() 시스템 호출이 발생할 때마다 실행됩니다. 
* 그런 다음 이 호출의 인수 (파일 이름 등)를 구문 분석하여이 정보를 BPF 맵에 작성합니다. 그런 다음 컴파일된 opensnoop.c 바이너리 부분 - 우리의 유저 스페이스 프로그램 (USP) -이 정보를 읽어서 STDOUT에 인쇄할 수 있습니다.


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

#### SEC("kprobe")  SEC("tracepoint")
```
SEC("kprobe/blk_account_io_start")
int BPF_KPROBE(blk_account_io_start, struct request *req){...}

SEC("kprobe/blk_account_io_done")
int BPF_KPROBE(blk_account_io_done, struct request *req){...}

SEC("kprobe/__blk_account_io_start")
int BPF_KPROBE(__blk_account_io_start, struct request *req){...}

SEC("kprobe/__blk_account_io_done")
int BPF_KPROBE(__blk_account_io_done, struct request *req){...}

SEC("tp_btf/block_io_start")
int BPF_PROG(block_io_start, struct request *req){...}

SEC("tp_btf/block_io_done")
int BPF_PROG(block_io_done, struct request *req){...}

SEC("tracepoint/syscalls/sys_enter_openat")
int tracepoint__syscalls__sys_enter_openat(struct trace_event_raw_sys_enter* ctx) {...}

SEC("tracepoint/syscalls/sys_enter_open")
int tracepoint__syscalls__sys_enter_open(struct trace_event_raw_sys_enter* ctx){...}

SEC("tracepoint/syscalls/sys_enter_openat")
int tracepoint__syscalls__sys_enter_openat(struct trace_event_raw_sys_enter* ctx){...}

SEC("tracepoint/syscalls/sys_exit_open")
int tracepoint__syscalls__sys_exit_open(struct trace_event_raw_sys_exit* ctx){...}

SEC("tracepoint/syscalls/sys_exit_openat")
int tracepoint__syscalls__sys_exit_openat(struct trace_event_raw_sys_exit* ctx){...}

SEC("tp_btf/block_rq_insert")
int block_rq_insert_btf(u64 *ctx){...}

SEC("tp_btf/block_rq_issue")
int block_rq_issue_btf(u64 *ctx){...}

SEC("tp_btf/block_rq_complete")
int BPF_PROG(block_rq_complete_btf, struct request *rq, int error, unsigned int nr_bytes){..}

SEC("raw_tp/block_rq_insert")
int BPF_PROG(block_rq_insert){...}

SEC("raw_tp/block_rq_issue")
int BPF_PROG(block_rq_issue){...}

SEC("raw_tp/block_rq_complete")
int BPF_PROG(block_rq_complete, struct request *rq, int error, unsigned int nr_bytes){...}



```

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


### bpftool prog list

```log
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
### bpftool map list
* 여기서 사용하는 map은 start, events 2개  
```log
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


  ## Add your won trace message 

eBPF 프로그램은 디버깅 목적으로 추적 메시지를 작성할 수 있습니다. 간단한 예제의 경우에는 일반적으로 /sys/kernel/debug/tracing/trace_pipe에서 읽을 수 있는 trace_pipe를 통해 수행됩니다. 그러나 이에는 몇 가지 제한 사항이 있습니다: 최대 3개의 인수, trace_pipe는 전역적으로 공유됩니다(따라서 동시에 실행되는 프로그램에서는 출력이 충돌할 수 있음) 등. 그러한 이유로, 생산적인 eBPF 코드에는 사용하지 않는 것이 좋습니다. 대신 BPF_PERF_OUTPUT() 인터페이스를 통해 수행해야 합니다. 그럼에도 불구하고, 이번 실습에서는 간단함을 위해 trace_pipe를 통해 수행하고 opensnoop에 자체 메시지를 추가합니다.


다음 문장을 opensnoop.bpf.c에 추가한다. 
 `bpf_printk("Hello world");`
 그리고 `make opensnoop` 하고 실행해 보면 .. 그리고 그 결과는  `cat /sys/kernel/debug/tracing/trace_pipe`를 통해서 확인한다. 

```sh
# cat /sys/kernel/debug/tracing/trace_pipe
```