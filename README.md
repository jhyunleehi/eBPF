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
### python 재거하면 ubuntu 오류 문제 발생한다. 
* python3 관련 된 패키지가 많기 때문에 아무것이나 삭제하면 좀 문제가 된다.
* ubuntu 22.4 버젼 기본 설치하고 나면 python3에서 설정된 내용은 다음과 같다. 

```
libpython3-dev/jammy-updates,jammy-security,now 3.10.6-1~22.04 amd64 [installed,automatic]
libpython3-stdlib/jammy-updates,jammy-security,now 3.10.6-1~22.04 amd64 [installed,automatic]
libpython3.10-dev/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
libpython3.10-minimal/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
libpython3.10-stdlib/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
libpython3.10/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
python3-apport/jammy-updates,jammy-updates,now 2.20.11-0ubuntu82.5 all [installed,automatic]
python3-apt/jammy-updates,now 2.4.0ubuntu3 amd64 [installed,automatic]
python3-aptdaemon.gtk3widgets/jammy,jammy,now 1.1.1+bzr982-0ubuntu39 all [installed,automatic]
python3-aptdaemon/jammy,jammy,now 1.1.1+bzr982-0ubuntu39 all [installed,automatic]
python3-bcrypt/jammy,now 3.2.0-1build1 amd64 [installed,automatic]
python3-blinker/jammy,jammy,now 1.4+dfsg1-0.4 all [installed,automatic]
python3-brlapi/jammy-updates,now 6.4-4ubuntu3 amd64 [installed,automatic]
python3-cairo/jammy,now 1.20.1-3build1 amd64 [installed,automatic]
python3-certifi/jammy,jammy,now 2020.6.20-1 all [installed,automatic]
python3-cffi-backend/jammy,now 1.15.0-1build2 amd64 [installed,automatic]
python3-chardet/jammy,jammy,now 4.0.0-1 all [installed,automatic]
python3-click/jammy,jammy,now 8.0.3-1 all [installed,automatic]
python3-colorama/jammy,jammy,now 0.4.4-1 all [installed,automatic]
python3-commandnotfound/jammy,jammy,now 22.04.0 all [installed,automatic]
python3-cryptography/jammy-updates,jammy-security,now 3.4.8-1ubuntu2.1 amd64 [installed,automatic]
python3-cups/jammy,now 2.0.1-5build1 amd64 [installed,automatic]
python3-cupshelpers/jammy,jammy,now 1.5.16-0ubuntu3 all [installed,automatic]
python3-dateutil/jammy,jammy,now 2.8.1-6 all [installed,automatic]
python3-dbus/jammy,now 1.2.18-3build1 amd64 [installed,automatic]
python3-debconf/jammy,jammy,now 1.5.79ubuntu1 all [installed,automatic]
python3-debian/jammy-updates,jammy-updates,now 0.1.43ubuntu1.1 all [installed,automatic]
python3-defer/jammy,jammy,now 1.0.6-2.1ubuntu1 all [installed,automatic]
python3-dev/jammy-updates,jammy-security,now 3.10.6-1~22.04 amd64 [installed,automatic]
python3-distro-info/jammy-updates,jammy-updates,now 1.1ubuntu0.2 all [installed,automatic]
python3-distro/jammy,jammy,now 1.7.0-1 all [installed,automatic]
python3-distupgrade/jammy-updates,jammy-updates,now 1:22.04.19 all [installed,automatic]
python3-distutils/jammy-updates,jammy-updates,jammy-security,jammy-security,now 3.10.8-1~22.04 all [installed,automatic]
python3-fasteners/jammy,jammy,now 0.14.1-2 all [installed,automatic]
python3-future/jammy-updates,jammy-updates,jammy-security,jammy-security,now 0.18.2-5ubuntu0.1 all [installed,automatic]
python3-gdbm/jammy-updates,jammy-security,now 3.10.8-1~22.04 amd64 [installed,automatic]
python3-gi-cairo/jammy-updates,now 3.42.1-0ubuntu1 amd64 [installed,automatic]
python3-gi/jammy-updates,now 3.42.1-0ubuntu1 amd64 [installed,automatic]
python3-httplib2/jammy,jammy,now 0.20.2-2 all [installed,automatic]
python3-ibus-1.0/jammy,jammy,now 1.5.26-4 all [installed,automatic]
python3-idna/jammy,jammy,now 3.3-1 all [installed,automatic]
python3-importlib-metadata/jammy,jammy,now 4.6.4-1 all [installed,automatic]
python3-jeepney/jammy,jammy,now 0.7.1-3 all [installed,automatic]
python3-jwt/jammy-updates,jammy-updates,jammy-security,jammy-security,now 2.3.0-1ubuntu0.2 all [installed,automatic]
python3-keyring/jammy,jammy,now 23.5.0-1 all [installed,automatic]
python3-launchpadlib/jammy,jammy,now 1.10.16-1 all [installed,automatic]
python3-lazr.restfulclient/jammy,jammy,now 0.14.4-1 all [installed,automatic]
python3-lazr.uri/jammy,jammy,now 1.0.6-2 all [installed,automatic]
python3-ldb/jammy-updates,jammy-security,now 2:2.4.4-0ubuntu0.22.04.2 amd64 [installed,automatic]
python3-lib2to3/jammy-updates,jammy-updates,jammy-security,jammy-security,now 3.10.8-1~22.04 all [installed,automatic]
python3-lockfile/jammy,jammy,now 1:0.12.2-2.2 all [installed,automatic]
python3-louis/jammy-updates,jammy-updates,jammy-security,jammy-security,now 3.20.0-2ubuntu0.2 all [installed,automatic]
python3-macaroonbakery/jammy-updates,jammy-updates,now 1.3.1-2ubuntu0.1 all [installed,automatic]
python3-mako/jammy-updates,jammy-updates,jammy-security,jammy-security,now 1.1.3+ds1-2ubuntu0.1 all [installed,automatic]
python3-markupsafe/jammy,now 2.0.1-2build1 amd64 [installed,automatic]
python3-minimal/jammy-updates,jammy-security,now 3.10.6-1~22.04 amd64 [installed,automatic]
python3-monotonic/jammy,jammy,now 1.6-2 all [installed,automatic]
python3-more-itertools/jammy,jammy,now 8.10.0-2 all [installed,automatic]
python3-nacl/jammy,now 1.5.0-2 amd64 [installed,automatic]
python3-netifaces/jammy,now 0.11.0-1build2 amd64 [installed,automatic]
python3-oauthlib/jammy-updates,jammy-updates,jammy-security,jammy-security,now 3.2.0-1ubuntu0.1 all [installed,automatic]
python3-olefile/jammy,jammy,now 0.46-3 all [installed,automatic]
python3-paramiko/jammy-updates,jammy-updates,jammy-security,jammy-security,now 2.9.3-0ubuntu1.2 all [installed,automatic]
python3-pexpect/jammy,jammy,now 4.8.0-2ubuntu1 all [installed,automatic]
python3-pil/jammy-updates,jammy-security,now 9.0.1-1ubuntu0.2 amd64 [installed,automatic]
python3-pip/jammy-updates,jammy-updates,jammy-security,jammy-security,now 22.0.2+dfsg-1ubuntu0.4 all [installed]
python3-pkg-resources/jammy-updates,jammy-updates,jammy-security,jammy-security,now 59.6.0-1.2ubuntu0.22.04.1 all [installed,automatic]
python3-problem-report/jammy-updates,jammy-updates,now 2.20.11-0ubuntu82.5 all [installed,automatic]
python3-protobuf/jammy-updates,jammy-security,now 3.12.4-1ubuntu7.22.04.1 amd64 [installed,automatic]
python3-ptyprocess/jammy,jammy,now 0.7.0-3 all [installed,automatic]
python3-pyatspi/jammy,jammy,now 2.38.2-1 all [installed,automatic]
python3-pymacaroons/jammy,jammy,now 0.13.0-4 all [installed,automatic]
python3-pyparsing/jammy,jammy,now 2.4.7-1 all [installed,automatic]
python3-renderpm/jammy-updates,jammy-security,now 3.6.8-1ubuntu0.1 amd64 [installed,automatic]
python3-reportlab-accel/jammy-updates,jammy-security,now 3.6.8-1ubuntu0.1 amd64 [installed,automatic]
python3-reportlab/jammy-updates,jammy-updates,jammy-security,jammy-security,now 3.6.8-1ubuntu0.1 all [installed,automatic]
python3-requests/jammy-updates,jammy-updates,jammy-security,jammy-security,now 2.25.1+dfsg-2ubuntu0.1 all [installed,automatic]
python3-rfc3339/jammy,jammy,now 1.1-3 all [installed,automatic]
python3-secretstorage/jammy,jammy,now 3.3.1-1 all [installed,automatic]
python3-setuptools/jammy-updates,jammy-updates,jammy-security,jammy-security,now 59.6.0-1.2ubuntu0.22.04.1 all [installed,automatic]
python3-six/jammy,jammy,now 1.16.0-3ubuntu1 all [installed,automatic]
python3-software-properties/jammy-updates,jammy-updates,now 0.99.22.9 all [installed,automatic]
python3-speechd/jammy-updates,jammy-updates,now 0.11.1-1ubuntu3 all [installed,automatic]
python3-systemd/jammy,now 234-3ubuntu2 amd64 [installed,automatic]
python3-talloc/jammy,now 2.3.3-2build1 amd64 [installed,automatic]
python3-tz/jammy-updates,jammy-updates,now 2022.1-1ubuntu0.22.04.1 all [installed,automatic]
python3-uno/jammy-updates,jammy-security,now 1:7.3.7-0ubuntu0.22.04.4 amd64 [installed,automatic]
python3-update-manager/jammy-updates,jammy-updates,now 1:22.04.18 all [installed,automatic]
python3-urllib3/jammy-updates,jammy-updates,jammy-security,jammy-security,now 1.26.5-1~exp1ubuntu0.1 all [installed,automatic]
python3-wadllib/jammy,jammy,now 1.3.6-1 all [installed,automatic]
python3-wheel/jammy-updates,jammy-updates,jammy-security,jammy-security,now 0.37.1-2ubuntu0.22.04.1 all [installed,automatic]
python3-xdg/jammy,jammy,now 0.27-2 all [installed,automatic]
python3-xkit/jammy,jammy,now 0.5.0ubuntu5 all [installed,automatic]
python3-yaml/jammy,now 5.4.1-1ubuntu1 amd64 [installed,automatic]
python3-zipp/jammy,jammy,now 1.0.0-3 all [installed,automatic]
python3.10-dev/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
python3.10-minimal/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
python3.10/jammy-updates,jammy-security,now 3.10.12-1~22.04.3 amd64 [installed,automatic]
python3/jammy-updates,jammy-security,now 3.10.6-1~22.04 amd64 [installed,automatic]
```


#### error
* ArgString 못찾는다.

```
Exception has occurred: ImportError       (note: full exception trace is shown but execution is paused at: _run_module_as_main)
cannot import name 'ArgString' from 'bcc' (/home/jhyunlee/.local/lib/python3.10/site-packages/bcc/__init__.py)
  File "/home/jhyunlee/code/eBPF/bcc/tools/opensnoop.py", line 24, in <module>
    from bcc import ArgString, BPF
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main (Current frame)
    return _run_code(code, main_globals, None,
ImportError: cannot import name 'ArgString' from 'bcc' (/home/jhyunlee/.local/lib/python3.10/site-packages/bcc/__init__.py)
```
===>> .local에 설정된  bcc 라이브러리를 제거한다. 

jhyunlee@Good:~/code/eBPF$ pip3 uninstall  bcc
Found existing installation: bcc 0.1.10
Uninstalling bcc-0.1.10:
  Would remove:
    /home/jhyunlee/.local/lib/python3.10/site-packages/bcc-0.1.10.dist-info/*
    /home/jhyunlee/.local/lib/python3.10/site-packages/bcc/*
Proceed (Y/n)? y
  Successfully uninstalled bcc-0.1.10

```
* 시스템에 설정된 bcc 라이브러리는 ... 0.29 버젼인데 
* .local에 설정된 버젼은  0.1.10 이라서 서로 차이가 있는 것 같다.
* .local을 제겅하면 global system 라이브러리 사용하면서 정상적으로 디버깅이 잘된다. 
```
root@Good:/usr/lib# find | grep bcc | grep dist
./python3/dist-packages/bcc-0.29.1+f7986688-py3.10.egg
```
