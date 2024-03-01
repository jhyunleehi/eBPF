# CO-RE compile once,run everywhere 

## BCC’s Approach to Portability

eBPF 프로그램의 기본적인 "Hello World" 예제를 보여주기 위해 BCC를 사용했습니다. BCC 프로젝트는 eBPF 프로그램을 구현하기 위한 최초의 인기 있는 프로젝트로, 커널 경험이 많지 않은 프로그래머들에게 비교적 접근하기 쉬운 사용자 공간 및 커널 측면의 프레임워크를 제공했습니다. 커널 간 이식성을 해결하기 위해 BCC는 대상 기계에서 런타임에서 eBPF 코드를 인접하게 컴파일하는 방식을 채택했습니다. 이 접근 방식에는 여러 가지 문제점이 있습니다:


• 코드를 실행하려는 각 대상 기계에는 컴파일 툴체인과 커널 헤더 파일이 설치되어 있어야 합니다. (기본적으로 항상 제공되지는 않음)
• 도구를 시작하기 전에 컴파일이 완료될 때까지 기다려야 하며, 이는 도구가 시작될 때마다 몇 초의 지연을 의미할 수 있습니다.
• 대규모로 동일한 기계 패밀리에서 도구를 실행하는 경우, 각 기계에서 컴파일을 반복하는 것은 컴퓨팅 자원의 낭비입니다.
• 일부 BCC 기반 프로젝트는 eBPF 소스 코드와 툴체인을 컨테이너 이미지로 패키징하여 각 기계에 배포를 쉽게 합니다. 그러나 커널 헤더가 존재하는지 확인하는 문제를 해결하지 않으며, 각 기계에 이러한 BCC 컨테이너가 여러 개 설치된 경우 중복이 더 발생할 수 있습니다.
• 임베디드 장치는 컴파일 단계를 실행할 충분한 메모리 자원을 갖고 있지 않을 수 있습니다.

그러게 실행 환경에서 매번 컴파일하는 것에 대한 부담감 때문에 go 언어 처럼 완전히 컴파일 된 바이너리 파일로 배포하는 방법을 좀 고민 했었지..

이러한 문제들로 인해 중요한 새로운 eBPF 프로젝트를 개발하려는 계획이 있다면 특히 다른 사람이 사용할 수 있도록 배포할 계획이 있다면 이전 BCC 접근 방식을 사용하지 않는 것을 권장하지 않습니다. 이 책에서는 기본적인 eBPF 개념에 대해 배우기에 좋은 접근 방식이기 때문에 BCC를 기반으로 한 몇 가지 예제를 제공했습니다. 특히 Python 사용자 공간 코드가 매우 간결하고 읽기 쉬워서입니다. 이 방법이 더 익숙하고 빠르게 무언가를 만들고 싶다면 이 방법 또한 완벽한 선택일 수 있습니다. 그러나 심각한 현대 eBPF 개발에는 최선의 접근 방식이 아닙니다.

## CO-RE Overview

#### BTF
 BTF (BPF Type Format)는 데이터 구조와 함수 시그니처의 레이아웃을 표현하는 형식입니다. CO-RE(Compile Once, Run Everywhere)에서는 컴파일 시간과 런타임에서 사용되는 구조체 간의 차이를 결정하는 데 사용됩니다. 또한 BTF는 bpftool과 같은 도구에서 데이터 구조를 인간이 읽을 수 있는 형식으로 덤프하는 데 사용됩니다. 5.4 버전부터 Linux 커널에서 BTF가 지원됩니다.

#### 커널 헤더
Linux 커널 소스 코드에는 사용하는 데이터 구조를 설명하는 헤더 파일이 포함되어 있으며, 이러한 헤더는 Linux의 버전 간에 변경될 수 있습니다. eBPF 프로그래머는 개별 헤더 파일을 포함할 수도 있고, 이 장에서 볼 수 있듯이 bpftool을 사용하여 실행 중인 시스템에서 vmlinux.h라는 헤더 파일을 생성할 수도 있습니다

#### 컴파일러 지원
Clang 컴파일러는 -g 플래그로 eBPF 프로그램을 컴파일할 때, 커널 데이터 구조를 설명하는 BTF 정보에서 유래된 CO-RE 재배치를 포함하도록 개선되었습니다. GCC 컴파일러도 12 버전에서 BPF 대상에 대한 CO-RE 지원을 추가했습니다.

#### 데이터 구조 재배치를 위한 라이브러리 지원
사용자 공간 프로그램이 eBPF 프로그램을 커널에 로드하는 시점에서 CO-RE 접근 방식은 컴파일될 때 존재하는 데이터 구조와 실행될 대상 시스템의 데이터 구조 간의 차이를 보상하기 위해 바이트코드를 조정해야 합니다. 이를 위해 몇 가지 라이브러리가 있습니다: libbpf는 이러한 재배치 기능을 포함한 최초의 C 라이브러리이며, Cilium eBPF 라이브러리는 Go 프로그래머를 위해 동일한 기능을 제공하며, Aya는 Rust를 위해 이를 수행합니다.

#### 옵션으로 BPF 스켈레톤
컴파일된 BPF 객체 파일에서 자동으로 스켈레톤을 생성할 수 있습니다. 이 스켈레톤에는 사용자 공간 코드가 BPF 프로그램의 라이프사이클을 관리하기 위해 호출할 수 있는 편리한 함수들이 포함되어 있습니다. 이 함수들은 커널에 로드하거나 이벤트에 연결하는 등의 작업을 수행할 수 있습니다. C로 작성된 사용자 공간 코드의 경우 bpftool gen skeleton으로 스켈레톤을 생성할 수 있습니다. 이러한 함수들은 개발자에게 기본 라이브러리(libbpf, cilium/ebpf 등)를 직접 사용하는 것보다 더 편리한 고수준 추상화입니다.


## BPF Type Format
BTF information describes how data structures and code are laid out in memory.
This information can be put to a variety of different uses.

CO-RE에 대해 논의하는 주된 이유는 eBPF 프로그램이 컴파일된 구조의 레이아웃과 실행될 위치의 차이를 알면 프로그램이 커널로 로드될 때 적절한 조정을 할 수 있기 때문입니다. 나중에 이 장에서 재배치 프로세스에 대해 논의할 것이지만, 지금은 BTF 정보가 활용될 수 있는 다른 몇 가지 용도도 고려해 보겠습니다.

구조체가 어떻게 레이아웃되어 있는지, 그리고 해당 구조체의 모든 필드의 유형을 알면 구조체의 내용을 사람이 읽을 수 있는 형태로 예쁘게 출력할 수 있습니다. 예를 들어, 문자열은 컴퓨터의 관점에서는 바이트의 시리즈에 불과하지만, 이러한 바이트를 문자로 변환하면 문자열이 사람들이 이해하기 훨씬 쉬워집니다. 이전 장에서 bpftool이 BTF 정보를 사용하여 맵 덤프의 출력을 형식화하는 예제를 이미 보았습니다.
BTF 정보에는 또한 번역된 또는 JIT된 프로그램 덤프의 출력과 소스 코드를 교차로 나타내도록 하는 라인 및 함수 정보도 포함되어 있습니다. 3장에서 보았듯이 bpftool은 이러한 기능을 사용합니다. 6장에 도달하면 검증기 로그 출력과 소스 코드 정보가 교차로 나타날 것입니다. 이 또한 BTF 정보에서 나온 것입니다.
BTF 정보는 BPF 스핀락에도 필요합니다. 스핀락은 두 개의 CPU 코어가 동시에 동일한 맵 값을 액세스하는 것을 막기 위해 사용됩니다. 이러한 잠금은 맵의 값 구조의 일부여야 합니다.


CO-RE에 대해 논의하는 주된 이유는 eBPF 프로그램이 컴파일된 구조의 레이아웃과 실행될 위치의 차이를 알면 프로그램이 커널로 로드될 때 적절한 조정을 할 수 있기 때문입니다. 나중에 이 장에서 재배치 프로세스에 대해 논의할 것이지만, 지금은 BTF 정보가 활용될 수 있는 다른 몇 가지 용도도 고려해 보겠습니다.
구조체가 어떻게 레이아웃되어 있는지, 그리고 해당 구조체의 모든 필드의 유형을 알면 구조체의 내용을 사람이 읽을 수 있는 형태로 예쁘게 출력할 수 있습니다. 예를 들어, 문자열은 컴퓨터의 관점에서는 바이트의 시리즈에 불과하지만, 이러한 바이트를 문자로 변환하면 문자열이 사람들이 이해하기 훨씬 쉬워집니다. 이전 장에서 bpftool이 BTF 정보를 사용하여 맵 덤프의 출력을 형식화하는 예제를 이미 보았습니다.

BTF 정보에는 또한 번역된 또는 JIT된 프로그램 덤프의 출력과 소스 코드를 교차로 나타내도록 하는 라인 및 함수 정보도 포함되어 있습니다. 3장에서 보았듯이 bpftool은 이러한 기능을 사용합니다. 6장에 도달하면 검증기 로그 출력과 소스 코드 정보가 교차로 나타날 것입니다. 이 또한 BTF 정보에서 나온 것입니다.
BTF 정보는 BPF 스핀락에도 필요합니다. 스핀락은 두 개의 CPU 코어가 동시에 동일한 맵 값을 액세스하는 것을 막기 위해 사용됩니다. 이러한 잠금은 맵의 값 구조의 일부여야 합니다.


### Listing BTF Information with bpftool
As with programs and maps, you can use the bpftool utility to show BTF information. 
The following command lists all the BTF data loaded into the kernel:

```
$ sudo bpftool btf list
1: name [vmlinux]  size 5775258B
2: name <anon>  size 1162B  prog_ids 2
3: name [hid]  size 8542B
...
147: name [nfnetlink]  size 2577B
159: name <anon>  size 1931B  prog_ids 434,432,433
	pids python(123587)
255: name <anon>  size 698B  prog_ids 543  map_ids 49
290: name <anon>  size 39654B
	pids bpftool(243814)


$ sudo bpftool prog show name hello
543: raw_tracepoint  name hello  tag 3d9eb0c23d4ab186  gpl
	loaded_at 2024-02-22T18:35:42+0900  uid 0
	xlated 80B  jited 68B  memlock 4096B  map_ids 49
	btf_id 255
```
#### bpftool btf dump 
```
root@Good:~# bpftool btf dump id  255
[1] PTR '(anon)' type_id=2
[2] STRUCT 'bpf_raw_tracepoint_args' size=0 vlen=1
	'args' type_id=5 bits_offset=0
[3] TYPEDEF '__u64' type_id=4
[4] INT 'unsigned long long' size=8 bits_offset=0 nr_bits=64 encoding=(none)
[5] ARRAY '(anon)' type_id=3 index_type_id=6 nr_elems=0
[6] INT '__ARRAY_SIZE_TYPE__' size=4 bits_offset=0 nr_bits=32 encoding=(none)
[7] FUNC_PROTO '(anon)' ret_type_id=8 vlen=1
	'ctx' type_id=1
[8] INT 'int' size=4 bits_offset=0 nr_bits=32 encoding=SIGNED
[9] FUNC 'hello' type_id=7 linkage=global
[10] FUNC_PROTO '(anon)' ret_type_id=8 vlen=1
	'ctx' type_id=1
[11] FUNC 'get_opcode' type_id=10 linkage=static
[12] CONST '(anon)' type_id=13
[13] INT 'char' size=1 bits_offset=0 nr_bits=8 encoding=SIGNED
[14] ARRAY '(anon)' type_id=12 index_type_id=6 nr_elems=12
[15] VAR 'hello.____fmt' type_id=14, linkage=static
[16] ARRAY '(anon)' type_id=13 index_type_id=6 nr_elems=13
[17] VAR 'LICENSE' type_id=16, linkage=global
[18] DATASEC '.rodata' size=12 vlen=1
	type_id=15 offset=0 size=12 (VAR 'hello.____fmt')
[19] DATASEC 'license' size=13 vlen=1
	type_id=17 offset=0 size=13 (VAR 'LICENSE')
```



리스트의 첫 번째 항목은 vmlinux이며, 이는 이전에 언급한 현재 실행 중인 커널에 대한 BTF 정보를 보유하는 vmlinux 파일에 해당합니다.


섹션 정의는 eBPF 프로그램이 어디에 연결되어야 하는지를 선언하고, 그런 다음 프로그램 자체가 이어집니다. 이전처럼, eBPF 프로그램 자체는 C 함수로 작성됩니다. 예제 코드에서는 이를 hello()라고 하며, 이전 장에서 보았던 hello() 함수와 매우 유사합니다. 이전 버전과 여기 버전 간의 차이를 고려해 보겠습니다:

```c
SEC("ksyscall/execve")
int BPF_KPROBE_SYSCALL(hello, const char *pathname)
{
struct data_t data = {};
struct user_msg_t *p;
data.pid = bpf_get_current_pid_tgid() >> 32;
data.uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
bpf_get_current_comm(&data.command, sizeof(data.command));
bpf_probe_read_user_str(&data.path, sizeof(data.path), pathname);
p = bpf_map_lookup_elem(&my_config, &data.uid);
if (p != 0) {
bpf_probe_read_kernel(&data.message, sizeof(data.message), p->message);
} else {
bpf_probe_read_kernel(&data.message, sizeof(data.message), message);
}
bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU,
&data, sizeof(data));
return 0;
}
```


# CO-RE eBPF Programs

