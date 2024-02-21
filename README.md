# eBPF


https://github.com/iovisor/bcc?tab=readme-ov-file


BPF 성능 분석 도구 - BPF 트레이싱을 통한 리눅스 시스템 관측가능성과 성능 향상  | 프로그래밍 인사이트 Programming Insight
브렌던 그레그 (지은이),이호연 (옮긴이)인사이트2021-07-26

### BPF Compiler Collection 
[BCC](https://github.com/iovisor/bcc?tab=readme-ov-file)


### vpftrace 

[bpftrace](https://github.com/bpftrace/bpftrace?tab=readme-ov-file)



[eBPF](https://ebpf.io/what-is-ebpf/)


Learning eBPF Tutorial 

[learning-ebpf-tutorial](https://isovalent.com/labs/learning-ebpf-tutorial/)


### eBPF 살펴보기

[eBPF살펴보기](https://velog.io/@hellonewtry/eBPF-%EC%82%B4%ED%8E%B4%EB%B3%B4%EA%B8%B0)


[XRP: In-Kernel Storage Functions with eBPF (OSDI 2022)](XRP: In-Kernel Storage Functions with eBPF (OSDI 2022))
[In-Kernel Storage Functions with eBPF](https://www.youtube.com/watch?v=n6_QaWATz2A)


[learn-ebpf-tracing](https://www.brendangregg.com/blog/2019-01-01/learn-ebpf-tracing.html)

[FS internals](https://www.youtube.com/watch?v=2SqPdM-YUaw&t=8s)



```sh
# apt install bpftrace 
# apt install bpfcc-tools
```

#### compile build

[https://www.flamingbytes.com/blog/how-to-install-bcc-on-ubuntu-22-04/](https://www.flamingbytes.com/blog/how-to-install-bcc-on-ubuntu-22-04/)



#### Linux Kernel Map

[kernel map](https://makelinux.github.io/kernel/map/)

## eBPF Applicatioon 

* [eBPF Applicaion](https://ebpf.io/applications/)
* Pixie 처럼 K8S 상태를 모니터링하는 기능을 참고하여 필요 기능 도출하는것.
* [Pyroscope](https://github.com/grafana/pyroscope)
결국 이것 처럼 구현하는 것이 목표가 될 것으로 예상 



### 접근 방법 
1. 정찬훈 책 BPF를 활용한 리눅스 시스템 트레이싱 구매
2. bcc/doc/reference.md 참고 --> python 또는 C 개발 
3. bcc/libbpf-tools  소스코드 참고
4. https://ebpf.io/blog/categories/technology/ 여기서 제공하는 기술 자료들
5. https://github.com/libbpf/libbpf
6. Learning eBPF pdf 
7. python ebpf --> monitoring 


### 모니터링 도구 golang 기반 
https://github.com/pixie-io/pixie
### 데이터 수집 처리 golang 
https://github.com/cilium/ebpf



## Ubunut - source 
To build the toolchain from source, one needs:

* LLVM 3.7.1 or newer, compiled with BPF support (default=on)
* Clang, built from the same tree as LLVM
* cmake (>=3.1), gcc (>=4.7), flex, bison
* LuaJIT, if you want Lua support
* Optional tools used in some examples: arping, netperf, and iperf
### build dependencies
* ubunut 22.04 jammy
```sh
$ sudo apt install -y zip bison build-essential cmake flex git libedit-dev \
  libllvm14 llvm-14-dev libclang-14-dev python3 zlib1g-dev libelf-dev libfl-dev python3-setuptools \
  liblzma-dev libdebuginfod-dev arping netperf iperf
```

### Install and compile BCC
```sh
$ git clone https://github.com/iovisor/bcc.git
$ mkdir bcc/build; cd bcc/build
$ cmake ..
$ make
$ sudo make install
$ cmake -DPYTHON_CMD=python3 .. # build python3 binding
$ pushd src/python/
$ make
$ sudo make install
$ popd
```

#### libbcc.so.0 undefined symbol bpf_module_create_b
```
root@good:/usr/share/bcc# cd tools
root@good:/usr/share/bcc/tools# ./opensnoop
Traceback (most recent call last):
  File "/usr/share/bcc/tools/./opensnoop", line 24, in <module>
    from bcc import ArgString, BPF
  File "/usr/lib/python3/dist-packages/bcc/__init__.py", line 27, in <module>
    from .libbcc import lib, bcc_symbol, bcc_symbol_option, bcc_stacktrace_build_id, _SYM_CB_TYPE
  File "/usr/lib/python3/dist-packages/bcc/libbcc.py", line 20, in <module>
    lib.bpf_module_create_b.restype = ct.c_void_p
  File "/usr/lib/python3.10/ctypes/__init__.py", line 387, in __getattr__
    func = self.__getitem__(name)
  File "/usr/lib/python3.10/ctypes/__init__.py", line 392, in __getitem__
    func = self._FuncPtr((name_or_ordinal, self))
AttributeError: /lib/x86_64-linux-gnu/libbcc.so.0: undefined symbol: bpf_module_create_b
```
==> 모든  python 모듈 설치 제거
==> bpf package 모두제거  
==> 그리고 재 설치 
```
# apt list | grep python | grep installed
# apt list | grep bpf | grep installed
```

### 기존 설치된  python 찌꺼기 모두 제거하고 다시 설치 한다. 


#### build dependencies
* ubunut 22.04 jammy
```sh
$ sudo apt install -y zip bison build-essential cmake flex git libedit-dev \
  libllvm14 llvm-14-dev libclang-14-dev python3 zlib1g-dev libelf-dev libfl-dev python3-setuptools \
  liblzma-dev libdebuginfod-dev arping netperf iperf

$ git clone https://github.com/iovisor/bcc.git
$ mkdir bcc/build; cd bcc/build
$ cmake ..
$ make
$ sudo make install
$ cmake -DPYTHON_CMD=python3 .. 
$ pushd src/python/
$ make
$ sudo make install
$ popd
```
