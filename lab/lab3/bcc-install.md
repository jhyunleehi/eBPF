# Ubuntu 에서 bcc 
The Ubuntu packages have slightly different names:
* iovisor packages use bcc in the name (e.g. bcc-tools)
*  Ubuntu packages use bpfcc (e.g. bpfcc-tools).

* ubunut 환경에서 default package로 제공되는 모듈인 bpf-tools는 뭔가 라이브러가 잘 안맞는 부분이 있다. 
* 따라서 아래 package 보다는 source를 다운 받아서 컴파일하고 install하는 방법이 정신 건강에 이롭다. 

## ubuntu package 설치 
Ubuntu Packages Source packages and the binary packages produced from them can be found at packages.ubuntu.com.
* ubunutu에서는 bpfcc-tools로 설치한다. 

```
$ sudo apt install bpfcc-tools linux-headers-$(uname -r)
$ sudo apt remove bpfcc-tools linux-headers-$(uname -r)
$ sudo apt installlinux-headers-$(uname -r)
```
* 설치되면 `/usr/sbin` 아래에 bcc 실행파일이 설치된다.  
```
# apt list | grep  bpfcc-tools
# apt show  bpfcc-tools

root@good:/usr/sbin# ls f*bpfcc
filelife-bpfcc  fileslower-bpfcc  filetop-bpfcc  funccount-bpfcc  funcinterval-bpfcc  funclatency-bpfcc  funcslower-bpfcc

root@good:/usr/sbin# ls e*bpfcc
execsnoop-bpfcc  exitsnoop-bpfcc  ext4dist-bpfcc  ext4slower-bpfcc

root@good:/usr/sbin# ls b*bpfcc
bashreadline-bpfcc  biolatency-bpfcc  biosnoop-bpfcc  bitesize-bpfcc  btrfsdist-bpfcc
bindsnoop-bpfcc     biolatpcts-bpfcc  biotop-bpfcc    bpflist-bpfcc   btrfsslower-bpfcc

```

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

$ sudo apt remove -y zip bison build-essential cmake flex git libedit-dev \
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


### error
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
