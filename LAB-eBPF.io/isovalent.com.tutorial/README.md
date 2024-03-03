# Learning eBPF Tutorial A hands-on lab by Isovalent

https://isovalent.com/resource-library/labs/

https://play.instruqt.com/embed/isovalent/tracks/tutorial-getting-started-with-ebpf/challenges/hello-world/notes?icp_a=amh5dW5sZWVoaUBnbWFpbC5jb20%3D&icp_fn=amVvbmcgaHl1bg%3D%3D&icp_ln=bGVl&auto_start=true

https://play.instruqt.com/embed/isovalent/tracks/tutorial-getting-started-with-ebpf/challenges/hello-world/assignment8

## bcc
The BCC framework provides macros that make it very easy to create maps. In this example the program creates a hash table, which stores key-value pairs, with this line:

* bcc macro
```
BPF_HASH(counter_table);
```

* python에서 hash map 참조하는 방법
 어차피 python으로 system program은 힘들기 때문에서 bcc 사용은 좀 고려를 해야 봐야 ...

```py
while True:
    sleep(2)
    s = ""
    for k,v in b["counter_table"].items():
        s += f"ID {k.value}: {v.value}\t"
    print(s)
```    

## bpftool
* hello.py 실행한 상태에서 
* bpftool 실행...

```t
# bpftool prog list
125: kprobe  name hello  tag f1db4e564ad5219a  gpl
        loaded_at 2024-03-03T07:46:52+0000  uid 0
        xlated 104B  jited 68B  memlock 4096B
        btf_id 49
        pids hello.py(2841)
```        

### 해설:
* kprobe에 attach 된것 확인 
* 라이센스는 gpl
* loading 시간, uid
* pid 2841

You can see that this is a program named hello attached to a kprobe. In this example, it has been given the ID 72 - yours might be different. It also has a tag, in this case f1db4e564ad5219a.

In the last line of this output you can see information about the user space process(es) that have references to this eBPF program. You can confirm that the process ID (2787 in my example output) matches what you see if you run ps -a:

```t
# ps -a | grep  2841
# bpftool prog show id 72
# bpftool prog show name hello
# bpftool prog show tag f1db4e564ad5219a
```
* byte code 
```t
# bpftool prog dump xlated name hello
```



### get map info 

```
cd learning-ebpf/chapter2/
./hello-map.py
```

```
# bpftool map show id $MAP_ID 
```

```t
# bpftool prog show name hello
127: kprobe  name hello  tag de24cf185ee252cd  gpl
        loaded_at 2024-03-03T07:58:40+0000  uid 0
        xlated 208B  jited 124B  memlock 4096B  map_ids 1   <-----
        btf_id 49
        pids hello-map.py(2899)

# export MAP_ID=1
# bpftool map show id $MAP_ID
1: hash  name counter_table  flags 0x0
        key 8B  value 8B  max_entries 10240  memlock 163840B
        btf_id 49
        pids hello-map.py(2899)

```
As expected, the map is of type hash, it has the name counter_table, and you can see that it is referred to by the user space process that's running hello-map.py.

You can also see that this map contains up to 10,240 entries of key-value pairs, where both the key and value are 8 bytes long. This matches the eBPF program code: if you look at the source code for hello-map.py again you'll see that both uid and counter local variables are 64-bit integers.


### read ebpf map 
* 여기서 uid가 0은 root 이므로 9개가 있다는 것..
* 값을 지정할때 8바이트를 이용해서 지정한다. 
* Little Endian 이라서 끝짜리수가 먼저 나오도록 지정 
* Note that you have to specify each of the 8 bytes of the key individually, starting with the least significant. You can use hex notation if you prefer, so all of the following are equivalent:
```
# bpftool map dump id $MAP_ID
[{
        "key": 0,
        "value": 4
    }
]

# bpftool map lookup id $MAP_ID key 0  0 0 0 0 0 0 0
{
    "key": 0,
    "value": 9
}

ID 105: 245     ID 0: 301       ID 1009: 13
ID 105: 245     ID 0: 301       ID 1009: 13

# bpftool map lookup id $MAP_ID key 105  0 0 0 0 0 0 0
{
    "key": 105,
    "value": 245
}

```

```t
 # bpftool map lookup id $MAP_ID key 100 0 0 0 0 0 0 0
 # bpftool map lookup id $MAP_ID key 0x64 0 0 0 0 0 0 0
 # bpftool map lookup id $MAP_ID key hex 64 0 0 0 0 0 0 0
 ```

### update ebpf map
* map 객체에 update도 가능하구나 
* 값을 지정할때 8바이트를 이용해서 지정한다. 
* Little Endian 이라서 끝짜리수가 먼저 나오도록 지정 
* key 255번에 2555 값을 지정하는 경우 
```t
root@server:~# bpftool map update  id $MAP_ID key 255 0 0 0 0 0 0 0 value 255 0 0 0 0 0 0 0

root@server:~# bpftool map lookup id $MAP_ID key 255 0 0 0 0 0 0 0
{
    "key": 255,
    "value": 255
}
```


## Network Packet 

chapter3에서 
* bpf/bpf_helpers.h는 BCC사용한다. macro 쓴다. 
```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

int counter = 0;

SEC("xdp")
int hello(struct xdp_md *ctx) {
    bpf_printk("Hello World %d", counter);
    counter++; 
    return XDP_PASS;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```
### 해설:
* global 변수  `int counter = 0;`
* 다음 줄은 eBPF 프로그램의 유형과 연결 지점을 정의하는 섹션 매크로입니다. 이는 네트워크 인터페이스에 연결되어 있으며 해당 인터페이스에서 수신된 인바운드 패킷이 발생할 때마다 트리거되는 XDP ("eXpress Data Path") 프로그램 유형입니다.
* 간단히 추적 라인을 생성하고 카운터를 증가시킨 다음 XDP_PASS를 반환하여 네트워크 패킷을 네트워크 스택으로 전달하도록 커널에 지시합니다.
* eBPF 검증기는 GPL 라이선스가 있는 BPF 헬퍼 함수를 호출하는 모든 프로그램에 대해 명시적으로 GPL 호환 라이선스가 선언되어 있는지 확인합니다. 
* BCC를 사용할 때는 이러한 것들을 BCC가 대신 처리합니다

### make 

```sh
root@server:~/learning-ebpf/chapter3# cat Makefile 
TARGETS = hello hello-func

all: $(TARGETS)
.PHONY: all

$(TARGETS): %: %.bpf.o 

%.bpf.o: %.bpf.c
        clang \
            -target bpf \
                -I/usr/include/$(shell uname -m)-linux-gnu \
                -g \
            -O2 -o $@ -c $<

clean: 
        - rm *.bpf.o
        - rm -f /sys/fs/bpf/hello 
        - rm -f /sys/fs/bpf/hello-func

root@server:~/learning-ebpf/chapter3# make hello
clang \
    -target bpf \
        -I/usr/include/x86_64-linux-gnu \
        -g \
    -O2 -o hello.bpf.o -c hello.bpf.c
```


### loading program into kernel 

```
# bpftool prog load hello.bpf.o /sys/fs/bpf/hello
# ls -l /sys/fs/bpf/
total 0
-rw------- 1 root root 0 Mar  3 08:56 hello

# ls -l /sys/fs/bpf/
total 0
-rw------- 1 root root 0 Mar  3 08:56 hello

# bpftool prog list
131: xdp  name hello  tag d35b94b4c0c10efb  gpl
        loaded_at 2024-03-03T08:56:07+0000  uid 0
        xlated 96B  jited 64B  memlock 4096B  map_ids 3,4
        btf_id 57
```        


### attach program to network interface 
* But at this point the program is not associated with any events that will trigger it. 
* The next command attaches it to the loopback network interface on this virtual machine.

```
# bpftool net attach xdp name hello dev lo

# bpftool net list
xdp:
lo(1) generic id 131

tc:

flow_dissector:

netfilter:
```
* 여기서 xdpgeneric/id: 131  eBPF program id이다. 
```
# ip a show dev lo
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 xdpgeneric/id:131 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
```       


### reading trace output

The eBPF program generates tracing in much the same way that the first "Hello World" example did, but this time we don't have a user space program to read the tracing and display it to us. Well, actually we do - this is another feature that bpftool provides. Here's the command to run to see any tracing being generated by any eBPF programs on this machine:

* term-1
```
# bpftool prog trace log

```
* term-2
```
# ping localhost
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.136 ms
64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.074 ms
64 bytes from localhost (127.0.0.1): icmp_seq=3 ttl=64 time=0.076 ms
64 bytes from localhost (127.0.0.1): icmp_seq=4 ttl=64 time=0.106 ms
64 bytes from localhost (127.0.0.1): icmp_seq=5 ttl=64 time=0.075 ms
64 bytes from localhost (127.0.0.1): icmp_seq=6 ttl=64 time=0.075 ms
64 bytes from localhost (127.0.0.1): icmp_seq=7 ttl=64 time=0.081 ms
64 bytes from localhost (127.0.0.1): icmp_seq=8 ttl=64 time=0.072 ms
^C
--- localhost ping statistics ---
8 packets transmitted, 8 received, 0% packet loss, time 7153ms
rtt min/avg/max/mdev = 0.072/0.086/0.136/0.021 ms
```
* term-1
```
# bpftool prog trace log
           <...>-3101    [003] d.s11  3292.668817: bpf_trace_printk: Hello World 0
           <...>-3101    [003] d.s11  3292.668843: bpf_trace_printk: Hello World 1
            ping-3101    [003] d.s11  3293.678304: bpf_trace_printk: Hello World 2
            ping-3101    [003] d.s11  3293.678340: bpf_trace_printk: Hello World 3
            ping-3101    [003] d.s11  3294.702255: bpf_trace_printk: Hello World 4
            ping-3101    [003] d.s11  3294.702291: bpf_trace_printk: Hello World 5
            ping-3101    [003] d.s11  3295.726243: bpf_trace_printk: Hello World 6
            ping-3101    [003] d.s11  3295.726280: bpf_trace_printk: Hello World 7
            ping-3101    [003] d.s11  3296.750039: bpf_trace_printk: Hello World 8
            ping-3101    [003] d.s11  3296.750075: bpf_trace_printk: Hello World 9
            ping-3101    [003] d.s11  3297.773938: bpf_trace_printk: Hello World 10
            ping-3101    [003] d.s11  3297.773974: bpf_trace_printk: Hello World 11
            ping-3101    [003] d.s11  3298.797869: bpf_trace_printk: Hello World 12
            ping-3101    [003] d.s11  3298.797905: bpf_trace_printk: Hello World 13
            ping-3101    [003] d.s11  3299.821773: bpf_trace_printk: Hello World 14
            ping-3101    [003] d.s11  3299.821809: bpf_trace_printk: Hello World 15
```

### local dev 연결해제
* 이렇게 수정하고 다시 컴파일 
```
SEC("xdp")
int hello(struct xdp_md *ctx) {
    bpf_printk("Hello World %d", counter);
    counter++; 
    return XDP_DROP; 
}
```
* 그리고 다시 `ping localhost` 실행

```
# bpftool net detach xdp  dev lo
# rm /sys/fs/bpf/hello
# ip link set dev lo xdp obj hello.bpf.o sec xdp
```


## pbf verifier
* 디버깅도 어려운데 verifier를 사용하지 않으면 어디서 어떻게 오류가 발생했는지 알수 없다. 

* chapter6

 커널에서 실행되는 몇 가지 eBPF 프로그램을 정의하는 hello-verifier.bpf.c가 포함되어 있습니다. 또한 이는 검증 프로세스를 실패시키는 변경 사항을 만들 때 실행되지 않습니다. 또한 이 예제에는 사용자 공간에서 eBPF 프로그램을 커널에 로드하고 이벤트에 연결하는 단계를 수행하는 사용자 공간 코드인 hello-verifier.c가 포함되어 있습니다. 대부분의 eBPF 응용 프로그램(Cilium 등)은 사용자가 직접 eBPF 프로그램을 커널에서 조작할 필요가 없도록 이와 같은 사용자 공간 로더 프로그램을 가지고 있습니다. 많은 사용자들은 bpftool과 같은 도구에 대해 심지어 인식할 필요가 없을 것입니다!

튜토리얼의 목적으로는 이 사용자 공간 코드에 대해 걱정할 필요가 없지만, 여분의 시간이 있다면 살펴볼만한 것입니다.

이 사용자 공간 코드의 한 가지 기능은 항상 eBPF 검증기의 출력을 표시하는 것입니다. 결과가 성공적으로 나올 때도 출력됩니다.


```sh
TARGET = hello-verifier
ARCH = $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')

BPF_TARGET = ${TARGET:=.bpf}
BPF_C = ${BPF_TARGET:=.c}
BPF_OBJ = ${BPF_TARGET:=.o}

USER_C = ${TARGET:=.c}
USER_SKEL = ${TARGET:=.skel.h}

COMMON_H = ${TARGET:=.h}

all: $(TARGET) $(BPF_OBJ)
.PHONY: all

$(TARGET): $(USER_C) $(USER_SKEL) $(COMMON_H)
	gcc -Wall -o $(TARGET) $(USER_C) -L../libbpf/src -l:libbpf.a -lelf -lz

$(BPF_OBJ): %.o: $(BPF_C) vmlinux.h  $(COMMON_H)
	clang \
	    -target bpf \
	    -D __BPF_TRACING__ \
        -D __TARGET_ARCH_$(ARCH) \
	    -Wall \
	    -O2 -g -o $@ -c $<
	llvm-strip -g $@

$(USER_SKEL): $(BPF_OBJ)
	bpftool gen skeleton $< > $@

vmlinux.h:
	bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

clean:
	- rm $(BPF_OBJ)
	- rm $(TARGET)
```

### license check 
bpf.c 코드에서  `char LICENSE[] SEC("license") = "Dual BSD/GPL";` 부분을 주석 처리한다.

그리고 실행을 해보면 Failed to load BPF object 에러가 발생한다. 

```log
root@server:~/learning-ebpf/chapter6# ./hello-verifier 
libbpf: prog 'kprobe_exec': BPF program load failed: Invalid argument
libbpf: prog 'kprobe_exec': failed to load: -22
libbpf: failed to load object 'hello_verifier_bpf'
libbpf: failed to load BPF skeleton 'hello_verifier_bpf': -22
...
cannot call GPL-restricted function from non-GPL compatible program
processed 34 insns (limit 1000000) max_states_per_insn 0 total_states 1 peak_states 1 mark_read 1
Failed to load BPF object
```

### bpf_map_lookup_elem 변수 오류

```sh
root@server:~/learning-ebpf/chapter6# ./hello-verifier 
libbpf: prog 'kprobe_exec': BPF program load failed: Permission denied
libbpf: prog 'kprobe_exec': failed to load: -13
libbpf: failed to load object 'hello_verifier_bpf'
libbpf: failed to load BPF skeleton 'hello_verifier_bpf': -13
reg type unsupported for arg#0 function kprobe_exec#23
...
; p = bpf_map_lookup_elem(&data, &uid);
31: (bf) r2 = r7                      ; R2_w=fp-48 R7_w=fp-48
32: (85) call bpf_map_lookup_elem#1
R1 type=fp expected=map_ptr
processed 31 insns (limit 1000000) max_states_per_insn 0 total_states 1 peak_states 1 mark_read 1
Failed to load BPF object
```
* `R1 type=fp expected=map_ptr` 이부분에서 map_prt를 요구하는데 fp 값이 안 맞다것...


### checking pointer dereferencing 
* pointer 역참조하기 전에 null 체크 하지 않으며 ...


라인 42와 45를 주석 처리하여 포인터를 명시적으로 null 여부를 확인하기 전에 참조하도록 변경하세요. 이로 인해 검증기 오류가 발생합니다. 'R7 invalid mem access 'map_value_or_null'' 검증기는 레지스터 7이 맵에서 검색된 값 또는 null을 보유하고 있으며, 이 값을 포인터로 사용하여 참조하려는 시도가 있음을 알고 있습니다. 이 값이 null일 가능성이 있으므로 이는 유효하지 않다고 판단되어 crash의 가능성이 없습니다.

시간이 있다면, 검증기 출력을 다시 추적하여 레지스터 7의 값이 할당되는 위치와 왜 이 값이 null일 수 있는지 확인하세요.

이 예제 프로그램이 검증기를 통과하지 못하도록 다른 방법도 있습니다. 자유롭게 탐색해 보세요! 'Learning eBPF'의 6장에서 이러한 실패가 발생하는 이유와 검증기의 출력을 해석하는 방법에 대해 자세히 알아볼 수 있습니다.

* null point를 미리 점검하지 않고 테스트 했더니 이런 오류 발생 
```
root@server:~/learning-ebpf/chapter6# ./hello-verifier 
...
; char a = p->message[0];
29: (71) r3 = *(u8 *)(r7 +0)
R7 invalid mem access 'map_value_or_null'
processed 28 insns (limit 1000000) max_states_per_insn 0 total_states 1 peak_states 1 mark_read 1
```

### outside array 

```
55: (71) r3 = *(u8 *)(r2 +0)
invalid access to map value, value_size=16 off=16 size=1
R2 max value is outside of the allowed memory range
processed 46 insns (limit 1000000) max_states_per_insn 0 total_states 3 peak_states 3 mark_read 1
Failed to load BPF object
```