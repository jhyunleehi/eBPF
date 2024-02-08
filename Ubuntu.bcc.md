# Ubuntu 에서 bcc 
The Ubuntu packages have slightly different names:
* iovisor packages use bcc in the name (e.g. bcc-tools)
*  Ubuntu packages use bpfcc (e.g. bpfcc-tools).

## ubuntu package 설치 
Ubuntu Packages Source packages and the binary packages produced from them can be found at packages.ubuntu.com.
* ubunutu에서는 bpfcc-tools로 설치한다. 

```
$ sudo apt-get install bpfcc-tools linux-headers-$(uname -r)
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