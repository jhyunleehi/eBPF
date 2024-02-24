## bpftool 컴파일 설치   
* /home/jhyunlee/code/eBPF/bcc/libbpf-tools/bpftool


```
$ git clone --recurse-submodules https://github.com/libbpf/bpftool.git
$ git submodule update --init
$ cd src
$ make
$ export  LANG=C
$ make
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  GEN      profiler.skel.h
  CC       prog.o
  CC       struct_ops.o
  CC       tracelog.o
  CC       xlated_dumper.o
  CC       disasm.o
  LINK     bpftool

$ sudo make install
[sudo] password for jhyunlee: 
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  INSTALL  bpftool
$ bpftool

Usage: bpftool [OPTIONS] OBJECT { COMMAND | help }
       bpftool batch file FILE
       bpftool version

       OBJECT := { prog | map | link | cgroup | perf | net | feature | btf | gen | struct_ops | iter }
       OPTIONS := { {-j|--json} [{-p|--pretty}] | {-d|--debug} |
                    {-V|--version} }

$ which bpftool
/usr/local/sbin/bpftool
```