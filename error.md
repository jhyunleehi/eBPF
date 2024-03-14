# Error list


### bpf2go compile error   
```
$(TARGET): $(USER_SKEL) 
	echo  go build...	
	go get github.com/cilium/ebpf/cmd/bpf2go
	go run github.com/cilium/ebpf/cmd/bpf2go  bpf ${TARGET}.c -- -I../headers
	go generate
	go build  
```

```
root@Good:~/go/src/ebpf-go/step09# make
clang \
    -target bpf \
        -D __TARGET_ARCH_x86 \
    -Wall \
    -O2 -g -o tcprtt.o -c tcprtt.c
llvm-strip -g tcprtt.o
bpftool gen skeleton tcprtt.o > tcprtt.skel.h
echo  go build...
go build...
go get github.com/cilium/ebpf/cmd/bpf2go
go run github.com/cilium/ebpf/cmd/bpf2go  bpf tcprtt.c -- -I../headers
/root/go/src/ebpf-go/step09/tcprtt.c:96:5: error: The eBPF is using target specific macros, please provide -target that is not bpf, bpfel or bpfeb
int BPF_KPROBE(vfs_open, struct path *path, struct file *file)
    ^
/root/go/src/ebpf-go/step09/bpf_tracing.h:461:20: note: expanded from macro 'BPF_KPROBE'
        return ____##name(___bpf_kprobe_args(args));                        \
                          ^
/root/go/src/ebpf-go/step09/bpf_tracing.h:441:2: note: expanded from macro '___bpf_kprobe_args'
        ___bpf_apply(___bpf_kprobe_args, ___bpf_narg(args))(args)
        ^
/root/go/src/ebpf-go/step09/bpf_helpers.h:157:29: note: expanded from macro '___bpf_apply'
#define ___bpf_apply(fn, n) ___bpf_concat(fn, n)
                            ^
note: (skipping 3 expansions in backtrace; use -fmacro-backtrace-limit=0 to see all)
/root/go/src/ebpf-go/step09/bpf_tracing.h:431:33: note: expanded from macro '___bpf_kprobe_args1'
        ___bpf_kprobe_args0(), (void *)PT_REGS_PARM1(ctx)
                                       ^
/root/go/src/ebpf-go/step09/bpf_tracing.h:341:29: note: expanded from macro 'PT_REGS_PARM1'
#define PT_REGS_PARM1(x) ({ _Pragma(__BPF_TARGET_MISSING); 0l; })
                            ^
<scratch space>:51:6: note: expanded from here
 GCC error "The eBPF is using target specific macros, please provide -target that is not bpf, bpfel or bpfeb"
     ^
/root/go/src/ebpf-go/step09/tcprtt.c:96:5: error: The eBPF is using target specific macros, please provide -target that is not bpf, bpfel or bpfeb
/root/go/src/ebpf-go/step09/bpf_tracing.h:461:20: note: expanded from macro 'BPF_KPROBE'
        return ____##name(___bpf_kprobe_args(args));                        \
                          ^
/root/go/src/ebpf-go/step09/bpf_tracing.h:441:2: note: expanded from macro '___bpf_kprobe_args'
        ___bpf_apply(___bpf_kprobe_args, ___bpf_narg(args))(args)
        ^
/root/go/src/ebpf-go/step09/bpf_helpers.h:157:29: note: expanded from macro '___bpf_apply'
#define ___bpf_apply(fn, n) ___bpf_concat(fn, n)
                            ^
note: (skipping 2 expansions in backtrace; use -fmacro-backtrace-limit=0 to see all)
/root/go/src/ebpf-go/step09/bpf_tracing.h:433:37: note: expanded from macro '___bpf_kprobe_args2'
        ___bpf_kprobe_args1(args), (void *)PT_REGS_PARM2(ctx)
                                           ^
/root/go/src/ebpf-go/step09/bpf_tracing.h:342:29: note: expanded from macro 'PT_REGS_PARM2'
#define PT_REGS_PARM2(x) ({ _Pragma(__BPF_TARGET_MISSING); 0l; })
                            ^
<scratch space>:53:6: note: expanded from here
 GCC error "The eBPF is using target specific macros, please provide -target that is not bpf, bpfel or bpfeb"
     ^
2 errors generated.
Error: can't execute clang: exit status 1
exit status 1
make: *** [Makefile:16: tcprtt] 오류 1
root@Good:~/go/src/ebpf-go/step09# 
```

#### fix it 
* only support -rageget amd64 
```Makefile 
$(TARGET): $(USER_SKEL) 
	echo  go build...	
	go get github.com/cilium/ebpf/cmd/bpf2go
    # go run github.com/cilium/ebpf/cmd/bpf2go -target bpfel  -type event bpf ${TARGET}.c -- -I../headers
    # go run github.com/cilium/ebpf/cmd/bpf2go -target bpfeb  -type event bpf ${TARGET}.c -- -I../headers
	go run github.com/cilium/ebpf/cmd/bpf2go -target amd64  -type event bpf ${TARGET}.c -- -I../headers
	go generate
	go build  
```

##  *btf.Pointer: not supported 
```sh
root@Good:~/go/src/ebpf-go/ex02-mount# go run github.com/cilium/ebpf/cmd/bpf2go -target amd64  -type event bpf mountsnoop.c -- -I../headers
Compiled /root/go/src/ebpf-go/ex02-mount/bpf_x86_bpfel.o
Stripped /root/go/src/ebpf-go/ex02-mount/bpf_x86_bpfel.o
Error: can't write /root/go/src/ebpf-go/ex02-mount/bpf_x86_bpfel.go: can't generate types: template: common:17:4: executing "common" at <$.TypeDeclaration>: error calling TypeDeclaration: Struct:"arg": field 2: type *btf.Pointer: not supported
exit status 1
root@Good:~/go/src/
```
==> remove 
* remove const char *  
```c
struct arg {
	__u64 ts;	
	__u64 flags;
	const char *src;  <<----- not support it 
	const char *dest;
	const char *fs;
	const char *data;
	enum op op;
};
```

```c
struct arg {
	__u64 ts;	
	__u64 flags;	
  __u64 src;    <<==== const char *  ---> const __u64
  __u64 dest;
  __u64 fs;
  __u64 data;
	enum op op;
};


static int probe_entry(const char *src, const char *dest, const char *fs,
                       __u64 flags, const char *data, enum op op) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = pid_tgid >> 32;
  __u32 tid = (__u32)pid_tgid;
  struct arg arg = {};

  if (target_pid && target_pid != pid)
    return 0;

  arg.ts = bpf_ktime_get_ns();
  arg.flags = flags;
  arg.src = (__u64)src;
  arg.dest = (__u64)dest;
  arg.fs = (__u64)fs;
  arg.data = (__u64)data;
  arg.op = op;
  bpf_map_update_elem(&args, &tid, &arg, BPF_ANY);
  return 0;
};
```





## collect C types: type name event: not found
```sh
root@Good:~/go/src/ebpf-go/ex02-mount# make
clang \
    -target bpf \
        -D __TARGET_ARCH_x86 \
    -Wall \
    -O2 -g -o mountsnoop.o -c mountsnoop.c
llvm-strip -g mountsnoop.o
bpftool gen skeleton mountsnoop.o > mountsnoop.skel.h
echo  go build...
go build...
go get github.com/cilium/ebpf/cmd/bpf2go
go run github.com/cilium/ebpf/cmd/bpf2go  -type event  bpf mountsnoop.c -- -I../headers
Compiled /root/go/src/ebpf-go/ex02-mount/bpf_bpfel.o
Stripped /root/go/src/ebpf-go/ex02-mount/bpf_bpfel.o
Error: collect C types: type name event: not found
exit status 1
make: *** [Makefile:16: mountsnoop] 오류 1
```
### fix 
* add it in pbf.c file
```c
const struct event *unused __attribute__((unused));
```




## C source files not allowed when not using cgo or SWIG: 
* check go file  

```sh
oot@Good:~/go/src/ebpf-go/ex02-mount# make
clang \
    -target bpf \
        -D __TARGET_ARCH_x86 \
    -Wall \
    -O2 -g -o mountsnoop.o -c mountsnoop.c
llvm-strip -g mountsnoop.o
bpftool gen skeleton mountsnoop.o > mountsnoop.skel.h
echo  go build...
go build...
go get github.com/cilium/ebpf/cmd/bpf2go
go run github.com/cilium/ebpf/cmd/bpf2go  -type event  bpf mountsnoop.c -- -I../headers
Compiled /root/go/src/ebpf-go/ex02-mount/bpf_bpfel.o
Stripped /root/go/src/ebpf-go/ex02-mount/bpf_bpfel.o
Wrote /root/go/src/ebpf-go/ex02-mount/bpf_bpfel.go
Compiled /root/go/src/ebpf-go/ex02-mount/bpf_bpfeb.o
Stripped /root/go/src/ebpf-go/ex02-mount/bpf_bpfeb.o
Wrote /root/go/src/ebpf-go/ex02-mount/bpf_bpfeb.go
# go run github.com/cilium/ebpf/cmd/bpf2go -target amd64  -type event bpf mountsnoop.c -- -I../headers
# go run github.com/cilium/ebpf/cmd/bpf2go -target amd64 bpf mountsnoop.c -- -I../headers
go generate
go build  
package ebpf-go/ex02-mount: C source files not allowed when not using cgo or SWIG: mountsnoop.c
make: *** [Makefile:20: mountsnoop] 오류 1
```

==>> c file don't need go build 
좀 허망하지만 go build할때 c 파일이 있으면 안된다는 것이다. 
그래서 해당 디렉토리에 c 파일을 제거하거나
주석으로 go build에서 제거한다고 표시를 해주면 된다. 
//go:build ignore

```c
//go:build ignore

/* SPDX-License-Identifier: GPL-2.0 */
/* Copyright (c) 2021 Hengqi Chen */
#include <vmlinux.h>
...
```




## bpf_trace_printk Error
* bpf_trace_printk 함수에서 에러 발생함 
```log
root@Good:~/go/src/ebpf-go/ex02-mount# sudo  ./ex02-mount 
2024/03/14 21:59:40 loading objects: field MountEntry: program mount_entry: load program: permission denied: 11: (85) call bpf_trace_printk#6: R2 type=map_value expected=scalar (17 line(s) omitted)
root@Good:~/go/src/ebpf-go/ex02-mount# sudo  ./ex02-mount 
2024/03/14 22:02:35 loading objects: field MountEntry: program mount_entry: load program: permission denied: 11: (85) call bpf_trace_printk#6: R2 type=map_value expected=scalar (17 line(s) omitted)
```

==> 원인은 함수 사용 가이드를 준수해야 한다. 
static long (*bpf_trace_printk)(const char *fmt, __u32 fmt_size, ...) = (void *) 6;
* 매개 변수는 적어도 3개가 되어야 한다. 

다음과 같이 함수를 사용해야 한다. 

```c
  int pid = bpf_get_current_pid_tgid() >> 32;
  const char fmt_str[] = "Hello, world, from BPF! My PID is [%d]";
  bpf_trace_printk(fmt_str, sizeof(fmt_str), pid);

  bpf_printk("===>> [%d]",pid);
```


==> 그리고 중요한것은 /sys/kernel/tracing/trace_pip를 통해서 로그를 실시간으로 받으려면
* trace_on 설정하고 나서 trace_pip를 모니터링 해야 한다.  
```
# echo 1 > /sys/kernel/debug/tracing/tracing_on
# cat      /sys/kernel/debug/tracing/trace_pip
```
===> https://nakryiko.com/posts/bpf-tips-printk/


## 

```
root@Good:~/go/src/ebpf-go/ex02-mount# sudo  ./ex02-mount 
2024/03/15 00:14:55 loading objects: field UmountExit: program umount_exit: load program: invalid argument: Unreleased reference id=5 alloc_insn=25 (162 line(s) omitted)
root@Good:~/go/src/ebpf-go/ex02-mount# 
```