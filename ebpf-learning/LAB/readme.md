# Learning eBPF

## 환경구성 

### 1. Building libbpf and installing header files

Libbpf is included as a submodule in this repo. You'll need to build and install
it for the C-based examples to build correctly. (See libbpf/README.md for more
details.)

* libbpf 라이브러리를 컴파일하고 설치한다. 
```sh
git clone --recurse-submodules https://github.com/lizrice/learning-ebpf
cd learning-ebpf
cd libbpf/src
make install 
cd ../..
```
* 이런 파일들이 설치된다.  
```
  INSTALL  bpf.h libbpf.h btf.h libbpf_common.h libbpf_legacy.h bpf_helpers.h bpf_helper_defs.h bpf_tracing.h bpf_endian.h bpf_core_read.h skel_internal.h libbpf_version.h usdt.bpf.h
  INSTALL  ./libbpf.pc
  INSTALL  ./libbpf.a ./libbpf.so ./libbpf.so.1 ./libbpf.so.1.0.1
```  

### 2. Building bpftool

There are several examples using `bpftool` throughout the book. To get a version
with libbfd support (which you'll need if you want to see the jited code in the 
Chapter 3 examples) you might need to build it from source:

```sh
cd ..
git clone --recurse-submodules https://github.com/libbpf/bpftool.git
cd bpftool/src 
make install 
```
* 생성된 vmlinux.h 파일을 복사한다. 
```
sudo cp bpftool/src/vmlinux.h /usr/include/vmlinux.h
```


`bpftool` binaries are now also available from https://github.com/libbpf/bpftool/releases these days.
```
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

## Examples
You won't be surprised to learn that the directories correspond to chapters in
the book. Here are the different examples that accompany each chapter.

* Chapter 1: What Is eBPF and Why Is It Important?
* [Chapter 2: eBPF's "Hello World"](../chapter2/README.md) - Basic examples using the BCC framework.
* [Chapter 3: Anatomy of an eBPF Program](../chapter3/README.md) - C-based XDP
  examples, used in the book to explore how the source code gets transformed to eBPF bytecode and
  machine code. There's also an example of BPF to BPF function calls.
* [Chapter 4: The bpf() System Call](../chapter4/README.md) - More BCC-based examples, used in the book to
  illustrate what's happening at the syscall level when you use eBPF.
* [Chapter 5: CO-RE, BTF and Libbpf](../chapter5/README.md) - Libbpf-based C
  example code.
* [Chapter 6: The eBPF Verifier](../chapter6/README.md) - Make small edits to the
  example code to cause a variety of verifier errors!
* [Chapter 7: eBPF Program and Attachment Types](../chapter7/README.md) - Examples
  of different eBPF program types.
* [Chapter 8: eBPF for Networking](../chapter8/README.md) - Example code that
  attaches to various points in the network stack to interfere with ping and
  curl requests. *Coming soon, load balancer example*
* Chapter 9: eBPF for Security - *coming soon*
* [Chapter 10: eBPF Programming](../chapter10/README.md) - The book explores examples from various eBPF
  libraries.
* Chapter 11: The Future Evolution of eBPF

### 주의 사항들 

#### 실행권한 : sudo -s 

You'll need root privileges (well, strictly CAP_BPF and [additional privileges](https://mdaverde.com/posts/cap-bpf/)) to be able to load BPF programs into the kernel. `sudo -s` is your friend.

#### View eBPF trace output

A couple of ways to see the output from the kernel's trace pipe where eBPF tracing gets written:

* `cat /sys/kernel/debug/tracing/trace_pipe`
* `bpftool prog tracelog`

### Installing on other Linux distributions
* Ubuntu 22.04 and a 5.15 kernel. 
* Clang 14. If you're using Clang 15 or later (which you can check with `clang --version` 
* BCC version 0.27.0  (https://github.com/iovisor/bcc/releases) 

