# CO-RE compile once,run everywhere 

지난 장에서 BTF(BPF 타입 포맷)를 처음 접했습니다. 이번 장에서는 BTF가 왜 필요하며, 어떻게 하면 eBPF 프로그램을 다양한 커널 버전 간에 이식 가능하게 만드는 데 사용되는지에 대해 논의합니다. BPF의 일회 컴파일, 어디서든 실행(CO-RE) 접근 방식의 중요한 부분입니다. 이는 서로 다른 커널 버전 간에 eBPF 프로그램을 이식하는 문제를 해결합니다.
많은 eBPF 프로그램이 커널 데이터 구조에 접근하며, eBPF 프로그래머는 해당 데이터 구조 내 필드를 올바르게 찾기 위해 관련된 Linux 헤더 파일을 포함해야 합니다. 그러나 Linux 커널은 지속적으로 개발되고 있기 때문에 내부 데이터 구조는 다른 커널 버전 간에 변경될 수 있습니다. 따라서 한 기계에서 컴파일된 eBPF 오브젝트 파일을 다른 커널 버전이 있는 기계에 로드한다면 데이터 구조가 동일할 보장이 없습니다.
CO-RE 접근 방식은 이러한 이식성 문제를 효율적으로 해결하는 큰 진전입니다. 이는 eBPF 프로그램이 컴파일된 데이터 구조 레이아웃에 대한 정보를 포함하도록 허용하며, 대상 기계에서 데이터 구조 레이아웃이 다른 경우 필드 액세스 방법을 조정하는 메커니즘을 제공합니다. 프로그램이 대상 기계의 커널에 존재하지 않는 필드나 데이터 구조에 액세스하려고 하는 경우를 제외하고는, 프로그램은 서로 다른 커널 버전 간에 이식 가능합니다.

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

CO-RE 접근 방식은 몇 가지 요소로 구성됩니다:

#### BTF
 BTF (BPF Type Format)는 데이터 구조와 함수 시그니처의 레이아웃을 표현하는 형식입니다. CO-RE(Compile Once, Run Everywhere)에서는 컴파일 시간과 런타임에서 사용되는 구조체 간의 차이를 결정하는 데 사용됩니다. 
 또한 BTF는 bpftool과 같은 도구에서 데이터 구조를 인간이 읽을 수 있는 형식으로 덤프하는 데 사용됩니다. 5.4 버전부터 Linux 커널에서 BTF가 지원됩니다.

* 현재 실행중인 커널 이미지에서 BTF 정보를 확인한다.  
* BTF 정보를 이용하여 libbpf는 BPF 코드를 실행하기 전에 재배치 작업을 수행한다. 재배치는 위의 테이블에 나열된 구조체와 필드가 현재 사용 중인 커널에서는 어떻게 구성되어 있는지 확인하면서 이루어진다.

```log
$ bpftool btf dump  file  /sys/kernel/btf/vmlinux format raw > BTF

$ vi BTF 
[80] STRUCT 'task_struct' size=9792 vlen=260
	'thread_info' type_id=140 bits_offset=0
	'__state' type_id=6 bits_offset=192
	'stack' type_id=63 bits_offset=256
	'usage' type_id=152 bits_offset=320
	'flags' type_id=6 bits_offset=352
	'ptrace' type_id=6 bits_offset=384
	'on_cpu' type_id=14 bits_offset=416
	...
	'thread' type_id=85 bits_offset=43008
```

#### 커널 헤더
Linux 커널 소스 코드에는 사용하는 데이터 구조를 설명하는 헤더 파일이 포함되어 있으며, 이러한 헤더는 Linux의 버전 간에 변경될 수 있습니다.
eBPF 프로그래머는 개별 헤더 파일을 포함할 수도 있고, 이 장에서 볼 수 있듯이 bpftool을 사용하여 실행 중인 시스템에서 vmlinux.h라는 헤더 파일을 생성할 수도 있습니다

#### 컴파일러 지원
Clang 컴파일러는 -g 플래그로 eBPF 프로그램을 컴파일할 때, 커널 데이터 구조를 설명하는 BTF 정보에서 유래된 CO-RE 재배치를 포함하도록 개선되었습니다. 
GCC 컴파일러도 12 버전에서 BPF 대상에 대한 CO-RE 지원을 추가했습니다.

#### 데이터 구조 재배치를 위한 라이브러리 지원
사용자 공간 프로그램이 eBPF 프로그램을 커널에 로드하는 시점에서 CO-RE 접근 방식은 컴파일될 때 존재하는 데이터 구조와 실행될 대상 시스템의 데이터 구조 간의 차이를 보상하기 위해 바이트코드를 조정해야 합니다. 
이를 위해 몇 가지 라이브러리가 있습니다: 
libbpf는 이러한 재배치 기능을 포함한 최초의 C 라이브러리이며, Cilium eBPF 라이브러리는 Go 프로그래머를 위해 동일한 기능을 제공하며, Aya는 Rust를 위해 이를 수행합니다.

#### 옵션으로 BPF 스켈레톤
컴파일된 BPF 객체 파일에서 자동으로 스켈레톤을 생성할 수 있습니다. 
이 스켈레톤에는 사용자 공간 코드가 BPF 프로그램의 라이프사이클을 관리하기 위해 호출할 수 있는 편리한 함수들이 포함되어 있습니다. 
이 함수들은 커널에 로드하거나 이벤트에 연결하는 등의 작업을 수행할 수 있습니다. C로 작성된 사용자 공간 코드의 경우 bpftool gen skeleton으로 스켈레톤을 생성할 수 있습니다. 이러한 함수들은 개발자에게 기본 라이브러리(libbpf, cilium/ebpf 등)를 직접 사용하는 것보다 더 편리한 고수준 추상화입니다.
* 뭔지는 모르겠지만 C로 작성된 뼈대 구조의 편리한 함수들이 있고, 이것은 커널에 로딩하거나 이벤트에 연결하는 역할을 한다
* 약간 bcc에서 제공하는 그런 기능을 macro로 제공하는 기능을 제공한다는 뜻인듯 

## BPF Type Format
BTF 정보는 데이터 구조와 코드가 메모리에 배치되는 방식을 설명합니다.
이 정보는 다양한 용도로 활용될 수 있습니다.

### BTF Use Cases 
CO-RE에 대해 논의하는 주된 이유는 eBPF 프로그램이 컴파일된 구조의 레이아웃과 실행될 위치의 차이를 알면 프로그램이 커널로 로드될 때 적절한 조정을 할 수 있기 때문입니다. 나중에 이 장에서 재배치 프로세스에 대해 논의할 것이지만, 지금은 BTF 정보가 활용될 수 있는 다른 몇 가지 용도도 고려해 보겠습니다.

구조체가 어떻게 레이아웃되어 있는지, 그리고 해당 구조체의 모든 필드의 유형을 알면 구조체의 내용을 사람이 읽을 수 있는 형태로 예쁘게 출력할 수 있습니다. 예를 들어, 문자열은 컴퓨터의 관점에서는 바이트의 시리즈에 불과하지만, 이러한 바이트를 문자로 변환하면 문자열이 사람들이 이해하기 훨씬 쉬워집니다. 이전 장에서 bpftool이 BTF 정보를 사용하여 맵 덤프의 출력을 형식화하는 예제를 이미 보았습니다.

BTF 정보에는 또한 번역된 또는 JIT된 프로그램 덤프의 출력과 소스 코드를 교차로 나타내도록 하는 라인 및 함수 정보도 포함되어 있습니다. 
3장에서 보았듯이 bpftool은 이러한 기능을 사용합니다. 
6장에 도달하면 검증기 로그 출력과 소스 코드 정보가 교차로 나타날 것입니다. 이 또한 BTF 정보에서 나온 것입니다.
BTF 정보는 BPF 스핀락에도 필요합니다. 스핀락은 두 개의 CPU 코어가 동시에 동일한 맵 값을 액세스하는 것을 막기 위해 사용됩니다. 이러한 잠금은 맵의 값 구조의 일부여야 합니다.

```
struct my_value {
    <other fields>
struct bpf_spin_lock lock;
    <other fields>
};
```

커널 내에서 eBPF 프로그램은 bpf_spin_lock() 및 bpf_spin_unlock() 도우미 함수를 사용하여 잠금을 획득하고 해제합니다. 이러한 도우미 함수는 잠금 필드가 구조체 내에서 어디에 있는지를 설명하는 BTF 정보가 사용 가능한 경우에만 사용할 수 있습니다.

BTF 정보의 유용성을 이해했으니, 몇 가지 구체적인 예시를 살펴보겠습니다.


### Listing BTF Information with bpftool

프로그램과 맵과 마찬가지로 bpftool 유틸리티를 사용하여 BTF 정보를 표시할 수 있습니다. 다음 명령은 커널에 로드된 모든 BTF 데이터를 나열합니다:

```
bpftool btf list
1: name [vmlinux] size 5843164B
2: name [aes_ce_cipher] size 407B
3: name [cryptd] size 3372B
...
149: name <anon> size 4372B prog_ids 319
pids hello-buffer-co(7660)
155: name <anon> size 37100B
```

리스트의 첫 번째 항목은 vmlinux이며, 이는 현재 실행 중인 커널에 대한 BTF 정보를 보유하는 vmlinux 파일에 해당합니다.

이 예시 출력을 얻기 위해, 제가 4장에서 실행 중인 hello-buffer-config 예제에서 이 명령을 실행했습니다. 149::로 시작하는 줄에서 이 프로세스가 사용하는 BTF 정보를 설명하는 항목을 볼 수 있습니다.

149: name <anon> size 4372B prog_ids 319 map_ids 103
   pids hello-buffer-co(7660)

Here’s what that line is telling us:
• This chunk of BTF information has ID 149.
• It’s an anonymous blob of around 4 KB of BTF information.
• It’s used by the BPF program with prog_id 319 and the BPF map with map_id 103.
• It’s also used by the process with ID 7660 (shown within parentheses) running
the hello-buffer-config executable (whose name has been truncated to 15 characters).


```sh
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
이 프로그램, 맵 및 BTF 식별자는 hello-buffer-config의 hello 프로그램에 대한 다음 출력과 일치합니다. bpftool이 보여주는 것입니다.

```
# bpftool prog show name hello

319: kprobe name hello tag a94092da317ac9ba gpl
      loaded_at 2022-08-28T14:13:35+0000 uid 0
      xlated 400B jited 428B memlock 4096B map_ids 103,104
      btf_id 149
      pids hello-buffer-co(7660)
```

이 두 세트의 정보 사이에 완전히 일치하지 않는 유일한 것은 프로그램이 추가적인 map_id인 104를 참조하는 것입니다. 
이것은 perf 이벤트 버퍼 맵이며, BTF 정보를 사용하지 않기 때문에 BTF 관련 출력에 나타나지 않습니다. 
bpftool은 프로그램과 맵의 내용을 덤프하는 것과 마찬가지로 데이터 덩어리에 포함된 BTF 유형 정보를 볼 때도 사용할 수 있습니다.


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
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(u32));
    __uint(value_size, sizeof(u32));
} output SEC(".maps");

struct user_msg_t {
   char message[12];
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, u32);
    __type(value, struct user_msg_t);
} my_config SEC(".maps");

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
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), p->message);
   } else {
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), message); 
   }

   bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, &data, sizeof(data));   
   return 0;
}

```


###  BTF Type 

BTF 정보의 ID를 알고 있다면 해당 내용을 확인할 수 있습니다. 
다음 명령을 사용하여 내용을 살펴봅니다: bpftool btf dump id <id>. 이전에 얻은 ID 149를 사용하여 실행한 결과, 총 69줄의 출력이 나왔습니다. 
각 줄은 유형 정의입니다. 여기서 처음 몇 줄을 설명하겠습니다. 
이 첫 몇 줄의 BTF 정보는 다음과 같이 소스 코드에서 정의된 config 해시 맵과 관련이 있습니다:
```c
struct user_msg_t {
   char message[12];
};

BPF_HASH(config, u32, struct user_msg_t);
```

