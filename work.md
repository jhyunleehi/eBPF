

### linux install and bpf compile 

```
$ uname -r
6.5.0-15-generic

jhyunlee@good:/kernel-src/samples/bpf$ git remote -v
origin	https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux.git (fetch)
origin	https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux.git (push)
jhyunlee@good:/kernel-src/samples/bpf$ git branch
* (HEAD v6.5 위치에서 분리됨)
  master

$ sudo apt install llvm
$ apt install llvm-dev

$ find /usr/include | grep libelf
/usr/include/libelf.h

```


### libelf.h 가 없다고...
=> 떡하니 있구만... 
```
jhyunlee@good:/kernel-src/samples/bpf$ find /usr/include | grep  libelf
/usr/include/libelf.h


jhyunlee@good:/kernel-src/samples/bpf$ apt list | grep  linux-header  | grep 설치

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

linux-headers-6.2.0-39-generic/jammy-updates,jammy-security,now 6.2.0-39.40~22.04.1 amd64 [설치됨,자동]
linux-headers-6.5.0-15-generic/jammy-updates,jammy-security,now 6.5.0-15.15~22.04.1 amd64 [설치됨]
linux-headers-6.5.0-17-generic/jammy-updates,jammy-security,now 6.5.0-17.17~22.04.1 amd64 [설치됨,자동]
linux-headers-generic-hwe-22.04/jammy-updates,jammy-security,now 6.5.0.17.17~22.04.9 amd64 [설치됨,자동]
```