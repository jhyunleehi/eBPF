# The eBPF Verifier

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