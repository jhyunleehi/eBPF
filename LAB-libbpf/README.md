# libbpf

https://github.com/libbpf/libbpf

Libbpf 신뢰할 수 있는 소스 코드는 linutools/lib/bpf 정기적으로 Github에 동기화됩니다. 
libbpf git 위치:  git://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git

### Libbpf 개발 참고 

* libbpf를 사용하여 BPF 애플리케이션을 구축하는 예는 libbpf-bootstrap 및  블로그 참고
* bcc아래에 있는  libbpf-tools는 실제 libbpf 좋은 예제
* BPF CO-RE 애플리케이션 구축의 실제적인 측면에 대한 내용은 "BPF CO-RE 참조 가이드"를 참조
* BPF 이식성 문제 및 BPF CO-RE 출처에 대한 일반적인 소개는 "BPF CO-RE"를 참조하세요.

* [LIBBPF API](https://libbpf.readthedocs.io/en/latest/api.html)
* [libbpf-bootstrap: demo BPF applications](https://github.com/libbpf/libbpf-bootstrap)
* [Building BPF applications with libbpf-bootstrap](https://nakryiko.com/posts/libbpf-bootstrap/)
* [BPF CO-RE reference guide](https://nakryiko.com/posts/bpf-core-reference-guide/)

* [BPF CO-RE (Compile Once – Run Everywhere)](https://nakryiko.com/posts/bpf-portability-and-co-re/)


* [BPF Portability and CO-RE](https://facebookmicrosites.github.io/bpf/blog/2020/02/19/bpf-portability-and-co-re.html)
* [HOWTO: BCC to libbpf conversion](https://facebookmicrosites.github.io/bpf/blog/2020/02/20/bcc-to-libbpf-howto-guide.html)
* [Tips & tricks for writing libbpf-tools](https://en.pingcap.com/blog/tips-and-tricks-for-writing-linux-bpf-applications-with-libbpf)


## [eBPF] CO-RE (Compile Once - Run Everywhere) 기능 분석

최근 몇 년간 리눅스 커널 커뮤니티에서 가장 주목받고 있는 기술은 누가 뭐래도 eBPF 일 것이다. 리눅스 커널에 안정성과 확장성, 그리고 생산성을 동시에 부여하는 혁신적인 기술로, 대표적인 쿠버네티스의 CNI 인 Cilium과 Falco, Pixie 등 다양한 오픈소스 프로젝트의 기반 기술로 이미 자리잡고 있으며, 점점 더 활용분야를 넓혀나가고 있다. 

### 왜 CO-RE가 필요한가?
아래 코드는 bcc 의 runqslower 예제코드 중 일부이다. 아래 함수는 리눅스 커널에서 문맥전환(context-switching)이 일어날때 실행되는 trace_sched_switch() 함수에서 호출되는 BPF 함수이다. (섹션 이름인 tp_btf/sched_switch 가 sched_switch 트레이스포인트에 해당 함수를 추가하라는 의미이다.)

 BPF 파일이 개발서버에서 앞에서 컴파일한 BPF 파일을 그대로 사용하다면 state 필드의 오프셋이 잘못되어있기 때문에 심각한 오류가 발생할 것이다. 기존에는 이러한 문제를 해결하기 위해 BPF 파일을 사용하는 서버에서 매번 직접 BPF 파일을 컴파일해서 사용을 했다. 하지만 BPF 파일을 컴파일하기 위해서는 clang/llvm 라이브러리를 항상 같이 배포해야하고, 컴파일하는데도 많은 자원과 시간이 소모된다. 이러한 문제를 해결하기 위해 나온 것이 CO-RE(Compile Once - Run Everywhere), 즉 한번 컴파일된 BPF 파일이 어디서든 실행되게 만드는 기술이다.

* 실행환경에서 커널구조가 개발환경과 달라질수 있기 때문에 실행환경에서 컴파일을 해야 한다. 

### CO-RE는  
BPF 파일의 실행을 준비하는 동안 현재 사용 중인 커널에서 동작할 수 있도록 몇 가지 작업을 하는 것
* 특정 구조체의 필드에 접근하는 모든 명령어를 현재 사용 중인 커널 설정에 맞게 변경하는 것
* BPF 파일에는 컴파일시 사용된 다양한 메타정보를 포함하고 있는 BTF(BPF Type Format)가 있다. 
* BTF 는 리눅스 커널에서 범용적이고 복잡한 DWARF 대신에 효율적으로 BPF 를 지원하기 위해 만든 것이다.

### BPF 파일의 BTF 확인 
* 현재 실행중인 커널 이미지에서 BTF 정보를 확인한다.  

```log
$ bpftool btf dump  file  /sys/kernel/btf/vmlinux format raw > BTF

$ vi BTF 
[80] STRUCT 'task_struct' size=9792 vlen=260
	'thread_info' type_id=140 bits_offset=0
	'__state' type_id=6 bits_offset=192
	'stack' type_id=63 bits_offset=256
	'usage' type_id=152 bits_offset=320
	'flags' type_id=6 bits_offset=352
	'ptrace' type_id=6 bits_offset=384
	'on_cpu' type_id=14 bits_offset=416
	...
	'thread' type_id=85 bits_offset=43008
```
* BTF 정보를 이용하여 libbpf는 BPF 코드를 실행하기 전에 재배치 작업을 수행한다. 재배치는 위의 테이블에 나열된 구조체와 필드가 현재 사용 중인 커널에서는 어떻게 구성되어 있는지 확인하면서 이루어진다.


### bpftool로 bpf program 확인하기  

```c
root@Good:/home/jhyunlee/code/eBPF/bcc# bpftool prog list
...
1069: tracing  name sched_wakeup  tag f227e542919646ad  gpl
        loaded_at 2024-03-01T23:30:37+0900  uid 0
        xlated 184B  jited 116B  memlock 4096B  map_ids 155,152
        btf_id 397
        pids runqslower(693474)
1071: tracing  name sched_wakeup_new  tag f227e542919646ad  gpl
        loaded_at 2024-03-01T23:30:37+0900  uid 0
        xlated 184B  jited 116B  memlock 4096B  map_ids 155,152
        btf_id 397
        pids runqslower(693474)
1072: tracing  name sched_switch  tag 6e659ccb41cb5d49  gpl
        loaded_at 2024-03-01T23:30:37+0900  uid 0
        xlated 992B  jited 573B  memlock 4096B  map_ids 155,152,153
        btf_id 397
        pids runqslower(693474)
```	

#### bpftool prg dump xlated id 1071

```c
root@Good:/home/jhyunlee/code/eBPF/bcc# bpftool prog dump xlated id  1071
int sched_wakeup_new(unsigned long long * ctx):
; int BPF_PROG(sched_wakeup_new, struct task_struct *p)
   0: (79) r1 = *(u64 *)(r1 +0)
; return trace_enqueue(p->tgid, p->pid);
   1: (61) r2 = *(u32 *)(r1 +2460)
; return trace_enqueue(p->tgid, p->pid);
   2: (61) r1 = *(u32 *)(r1 +2456)
   3: (63) *(u32 *)(r10 -4) = r1
; if (!pid)
   4: (15) if r1 == 0x0 goto pc+16
; if (targ_tgid && targ_tgid != tgid)
   5: (18) r3 = map[id:155][0]+12
   7: (61) r4 = *(u32 *)(r3 +0)
; if (targ_pid && targ_pid != pid)
   8: (18) r2 = map[id:155][0]+8
  10: (61) r3 = *(u32 *)(r2 +0)
; ts = bpf_ktime_get_ns();
  11: (85) call bpf_ktime_get_ns#235216
; ts = bpf_ktime_get_ns();
  12: (7b) *(u64 *)(r10 -16) = r0
  13: (bf) r2 = r10
; ts = bpf_ktime_get_ns();
  14: (07) r2 += -4
  15: (bf) r3 = r10
  16: (07) r3 += -16
; bpf_map_update_elem(&start, &pid, &ts, 0);
  17: (18) r1 = map[id:152]
  19: (b7) r4 = 0
  20: (85) callroot@Good:/home/ htab_map_update_elem#278848
; int BPF_PROG(sched_wakeup_new, struct task_struct *p)
  21: (b7) r0 = 0
  22: (95) exit
```



#### 코드 보기
* BPF_PROG는 macro이고, static sched_switch 함수 생성한다. 

* 파일의 위치 
    - hyunlee@Good:~/code$ find | grep runqslower.bpf.c
    - ./linux/tools/bpf/runqslower/runqslower.bpf.c
    - ./bcc/libbpf-tools/runqslower.bpf.c

* 컴파일 준비
```
* build dependencies
* ubunut 22.04 jammy
```sh
$ sudo apt install -y zip bison build-essential cmake flex git libedit-dev \
  libllvm14 llvm-14-dev libclang-14-dev python3 zlib1g-dev libelf-dev libfl-dev python3-setuptools \
  liblzma-dev libdebuginfod-dev arping netperf iperf

$ cd  /home/jhyunlee/code/bcc/libbpf-tools
$ make  runqslower

```
- "$@" 또는 "$(@)"는 바로 Target 을 말합니다. 
- "$<"는 열거된 Depend중에 가장 왼쪽에 기술된 1개의 Depend를 말하며 "$^"는 Depend 전체를 
- ${Q}는 특수문제 억제하기 위해서 사용 


```c
SEC("tp_btf/sched_switch")
int BPF_PROG(sched_switch, bool preempt, struct task_struct *prev, struct task_struct *next)
{
	return handle_switch(ctx, prev, next);
}


static int handle_switch(void *ctx, struct task_struct *prev, struct task_struct *next)
{
	struct event event = {};
	u64 *tsp, delta_us;
	u32 pid;

	/* ivcsw: treat like an enqueue event and store timestamp */
	if (get_task_state(prev) == TASK_RUNNING)
		trace_enqueue(BPF_CORE_READ(prev, tgid), BPF_CORE_READ(prev, pid));

	pid = BPF_CORE_READ(next, pid);

	/* fetch timestamp and calculate delta */
	tsp = bpf_map_lookup_elem(&start, &pid);
	if (!tsp)
		return 0;   /* missed enqueue */

	delta_us = (bpf_ktime_get_ns() - *tsp) / 1000;
	if (min_us && delta_us <= min_us)
		return 0;

	event.pid = pid;
	event.prev_pid = BPF_CORE_READ(prev, pid);
	event.delta_us = delta_us;
	bpf_probe_read_kernel_str(&event.task, sizeof(event.task), next->comm);
	bpf_probe_read_kernel_str(&event.prev_task, sizeof(event.prev_task), prev->comm);

	/* output */
	bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
			      &event, sizeof(event));

	bpf_map_delete_elem(&start, &pid);
	return 0;
}

#define BPF_PROG(name, args...)						    \
..
____##name(unsigned long long *ctx, ##args)

```

#### readelf

```sh
$ file  .output/runqslower.bpf.o
.output/runqslower.bpf.o: ELF 64-bit LSB relocatable, eBPF, version 1 (SYSV), not stripped

$ readelf --section-details --headers .output/runqslower.bpf.o

$ objdump -x  .output/runqslower.bpf.o


```

The object file is in ELF format. ELF stands for "Executable and Linkable Format" and it represents a common standard file format for executable files, object code, shared libraries, and core dumps. It's also the standard file format for binary files on x86 processors.

A few interesting things to observe:

Machine is Linux BPF. Hence, this binary code is meant to be run inside the BPF in-kernel virtual machine.
There is BTF information included in this file. BTF is the metadata format which encodes the debug info related to BPF programs/maps. This debug info is used for map pretty print, function signatures, etc.
After the section header named .text in the table, there are four executable sections starting with tracepoint. These correspond to four BPF programs.


Let's find those four programs in the BPF source code. In the second tab, </> Editor, you can open the file opensnoop.bpf.c - our kernel-space program (KSP). Scroll down to find four different functions with names beginning with int tracepoint__syscalls.... You should find them on lines 50, 68, 125 and 131.

Each of these is preceded by a SEC() macro which corresponds to the executable sections listed by readelf. It defines the eBPF hook where the code should be attached to (SEC("tracepoint/<category>/<name>")). In our case to the eBPF tracepoints sys_enter_open and sys_enter_openat, as our eBPF code should be called whenever a open and openat syscall is issued ("entered", therefore sys_enter). Tracepoints are static markers in the kernel’s code that you can use to attach (eBPF) code in a running kernel. These tracepoint are often placed in locations which are interesting or common locations to measure performance.
The tracepoint__syscalls__sys_enter_open and tracepoint__syscalls__sys_enter_openat functions get executed whenever a open()/openat() syscall is issued. They then parse the arguments (filename, etc.) of the call and write this information to the BPF map. From there, our compiled opensnoop.c binary part - our user-space program (USP) - can read and print it to STDOUT.
If you'd like to get even more details about what these four BPF programs are doing, refer to chapter 3 of the book "What is eBPF" by Liz Rice.

But how does this fit together with the Linux kernel? Click on Next to find out in the next section.




