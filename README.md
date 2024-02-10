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



### hello.c

#### perf 

```sh
$ vi hello.c
#include <stdio.h>
int VAL=0;
int main(){
    for (int i=0;i<10;i++){
          printf("hello worldi [%d]\n", i);
    }
    return 0;
}

$ gcc -g -pg -o hello hello.c
$ ./hello
$ file ./hello
$ ldd  ./hello$ 
$ hexdump -C  ./hello | head -4
$ xxd ./hello 
$ readelf -h ./hello 
$ readelf -l ./hello
$ objdump -d ./hello | more 
$ objdump -x ./hello | more 
$ gdb  ./hello 
(gdb) list
(gdb) break 5
(gdb) run 
(gdb) info frame
(gdb) info files 
(gdb) info local 
(gdb) info proc
(gdb) info break 
(gdb) print VAL
(gdb) display i
(gdb) disas main

$ stat ./hello
$ perf record -a -g  ./hello
$ perf report --header  -F overhead,comm,parent
$ perf stat ./hello
$ strace ./hello 
$ stat  ./hello
$ sudo uftrace -K 5 ./hello
$ sudo uftrace record -K 5 ./hello
$ sudo uftrace tui 
```