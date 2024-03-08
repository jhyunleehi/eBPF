# CO-RE compile once,run everywhere 

지난 장에서 BTF(BPF 타입 포맷)를 처음 접했습니다. 이번 장에서는 BTF가 왜 필요하며, 어떻게 하면 eBPF 프로그램을 다양한 커널 버전 간에 이식 가능하게 만드는 데 사용되는지에 대해 논의합니다. BPF의 일회 컴파일, 어디서든 실행(CO-RE) 접근 방식의 중요한 부분입니다. 이는 서로 다른 커널 버전 간에 eBPF 프로그램을 이식하는 문제를 해결합니다.
많은 eBPF 프로그램이 커널 데이터 구조에 접근하며, eBPF 프로그래머는 해당 데이터 구조 내 필드를 올바르게 찾기 위해 관련된 Linux 헤더 파일을 포함해야 합니다. 그러나 Linux 커널은 지속적으로 개발되고 있기 때문에 내부 데이터 구조는 다른 커널 버전 간에 변경될 수 있습니다. 따라서 한 기계에서 컴파일된 eBPF 오브젝트 파일을 다른 커널 버전이 있는 기계에 로드한다면 데이터 구조가 동일할 보장이 없습니다.
CO-RE 접근 방식은 이러한 이식성 문제를 효율적으로 해결하는 큰 진전입니다. 이는 eBPF 프로그램이 컴파일된 데이터 구조 레이아웃에 대한 정보를 포함하도록 허용하며, 대상 기계에서 데이터 구조 레이아웃이 다른 경우 필드 액세스 방법을 조정하는 메커니즘을 제공합니다. 프로그램이 대상 기계의 커널에 존재하지 않는 필드나 데이터 구조에 액세스하려고 하는 경우를 제외하고는, 프로그램은 서로 다른 커널 버전 간에 이식 가능합니다.

eBPF CO-RE (Compile Once, Run Everywhere)는 eBPF 프로그램을 다양한 커널 버전에서 포터블하게 실행할 수 있도록 하는 기술적 접근 방식입니다. 
CO-RE는 eBPF 프로그램을 컴파일할 때 해당 프로그램이 사용할 커널 데이터 구조의 레이아웃에 대한 정보를 포함하도록 합니다. 그러면 커널이 eBPF 프로그램을 로드할 때 커널의 데이터 구조와 일치하도록 프로그램을 조정할 수 있습니다.

CO-RE의 주요 아이디어는 커널이 eBPF 프로그램을 로드하는 시점에 프로그램의 바이너리를 수정하고 적절한 조정을 수행하여 프로그램이 다양한 커널 환경에서 올바르게 작동하도록 하는 것입니다. 이를 통해 개발자는 특정 커널 버전에 종속되지 않고도 동일한 eBPF 프로그램을 여러 환경에서 실행할 수 있습니다.

CO-RE는 BTF (BPF Type Format) 정보를 활용하여 작동합니다. BTF는 커널의 데이터 구조와 관련된 정보를 포함하고 있으며, 이 정보를 사용하여 eBPF 프로그램이 해당 데이터 구조와 상호 작용하는 방식을 파악할 수 있습니다. 따라서 CO-RE는 BTF 정보를 사용하여 프로그램이 로드되는 커널 환경에 맞게 프로그램을 조정합니다.

이러한 CO-RE 접근 방식은 eBPF 프로그램의 포터빌리티를 향상시키고, 다양한 환경에서 일관된 동작을 보장합니다. 따라서 새로운 커널 버전이 출시될 때마다 기존의 eBPF 프로그램을 재컴파일할 필요 없이 그대로 사용할 수 있습니다.



다음은 eBPF CO-RE의 작동 방식을 자세히 설명하는 예시입니다.

1. 커널 데이터 구조와의 호환성 확인: CO-RE는 eBPF 프로그램이 사용할 커널 데이터 구조의 레이아웃을 확인합니다. 이 데이터 구조는 예를 들어 네트워크 패킷 헤더, 시스템 콜 매개 변수, 또는 커널 내부의 다른 중요 정보일 수 있습니다.

2. BTF 정보 수집: CO-RE는 BTF 정보를 사용하여 커널의 데이터 구조를 분석합니다. BTF는 커널 데이터 구조의 유형, 필드 및 멤버에 대한 정보를 포함하고 있으며, 이를 통해 eBPF 프로그램이 커널 데이터에 액세스하는 방법을 이해할 수 있습니다.

3. 프로그램 로드 및 조정: eBPF 프로그램을 컴파일하는 동안 CO-RE는 BTF 정보를 포함하여 프로그램을 생성합니다. 커널은 이 프로그램을 로드할 때 프로그램의 BTF 정보를 분석하고, 해당 커널의 데이터 구조와 일치하도록 프로그램을 조정합니다.

4. 실행 환경에서의 프로그램 실행: 로드된 eBPF 프로그램은 커널 내에서 실행됩니다. 이 프로그램은 로드된 커널의 데이터 구조와 호환되며, 따라서 프로그램이 올바르게 작동하고 예상대로 동작합니다.

5. 호환성 보장: CO-RE는 다양한 커널 버전에서 동일한 eBPF 프로그램이 작동하도록 보장합니다. 새로운 커널 버전이 출시될 때마다 프로그램을 다시 컴파일할 필요 없이 기존 프로그램을 계속해서 사용할 수 있습니다.

6. 유연성 및 이식성: CO-RE를 사용하면 개발자는 특정 커널 버전에 종속되지 않고도 eBPF 프로그램을 여러 환경에서 실행할 수 있습니다. 이는 코드를 유지 관리하고 업데이트하는 데 필요한 노력을 줄이며, 새로운 기능을 더 쉽게 추가할 수 있음을 의미합니다.

이러한 방식으로 CO-RE는 eBPF 프로그램의 이식성과 유연성을 향상시키며, 개발자가 다양한 커널 환경에서 프로그램을 개발하고 배포하는 것을 용이하게 합니다.


다음은 CO-RE를 사용하여 eBPF 프로그램을 작성하고 컴파일하는 예시 코드입니다. 이 코드는 BPF Type Format (BTF) 정보를 포함하여 eBPF 프로그램을 컴파일하고, 커널에서 실행될 때 자동으로 조정되도록 합니다.

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

CO-RE 접근 방식은 몇 가지 요소로 구성된다.  

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

* 여기서 btf_id 140번 , map_id는 20,19번

```
# bpftool prog list
160: kprobe  name hello  tag 2b77904d73f76a56  gpl
	loaded_at 2024-03-05T09:27:32+0900  uid 0
	xlated 368B  jited 203B  memlock 4096B  map_ids 20,19
	btf_id 140
	pids hello-buffer-co(216139)


# bpftool btf list
140: name <anon>  size 2292B  prog_ids 160  map_ids 20
	pids hello-buffer-co(216139)
```
* kprobe의 name은 "hello" 이것은 kprobe 핸들러의 이름이라서...
SEC("ksyscall/execve")
int BPF_KPROBE_SYSCALL(hello, const char *pathname)
* 여기서는  `bpf btf dump id 140` 이용하여  확인
* 이 해시 테이블은 u32 타입의 키와 구조체 user_msg_t 타입의 값을 가진다.
* 12바이트 메시지 필드를 유지하는 것이다.
* BTF(Binary Type Format)는 ELF(Executable and Linkable Format) 파일과 같은 바이너리 파일에서 변수와 함수의 타입을 설명하는데 사용되는 포맷이다. 디버거 및 프로파일러와 같은 도구는 소스 코드에 대한 액세스 없이 프로그램의 변수 및 함수 유형을 이해할 수 있게 해준다.


```
# bpftool btf  dump id 140
[1] TYPEDEF 'u32' type_id=2
[2] TYPEDEF '__u32' type_id=3
[3] INT 'unsigned int' size=4 bits_offset=0 nr_bits=32 encoding=(none)
...
```

각 줄의 시작 부분에 대괄호로 묶인 숫자는 타입 ID를 나타내며, 첫 번째 줄 [1]은 타입 ID 1을 정의하고, 그 다음 줄들은 해당 타입 ID를 참조하여 타입을 정의한다.

• 타입 1은 u32라는 타입을 정의하며, 이 타입의 실제 타입은 타입 ID 2, 즉 두 번째 줄에서 정의된 타입이다. 앞서 언급했듯이, 이 해시 테이블의 키는 u32 타입을 사용한다.
• 타입 2는 __u32라는 이름을 가지며, 이 타입의 실제 타입은 타입 ID 3이다.
• 타입 3은 4바이트 길이의 unsigned int라는 이름의 정수형 타입이다.

이 세가지 타입은 모두 32비트 unsigned 정수형 타입의 다른 이름들이다. 
* C언어에서는 정수의 길이가 플랫폼에 종속되기 때문에, Linux에서는 특정 길이를 갖는 정수를 명시하기 위해 u32와 같은 타입을 사용한다. 
* 이 시스템에서는 u32가 unsigned 정수형에 해당한다. 
* 이러한 타입을 참조하는 사용자 공간 코드는 _u32와 같이 언더스코어()로 시작하는 이름을 사용해야 한다.

==> 이것이 뭔가 실제 데이터 타입 정보를 정의해 두어서 runtime에 맞게 그 데이터 타입으로 실행될 수 있도록 한다 이런것 이구나. 그래서 이것은 데이터 타입을 계층적으로 자기 자신을 설명하는 구조로 되어 있구나. 
==> 그래서 vmlinux.h 에 정의되어 있는것을 보면 다음과 같다. 사용자 영역에서는 __32를 사용하고 이것은 u32로 리눅스 안에서는 사용된다. 
typedef는 A는 B이다 방식으로 `typedef struct node *pnode;` 이런 식으로 정의된다. 
```c
typedef __s8 s8;
typedef __u8 u8;
typedef __s16 s16;
typedef __u16 u16;
typedef __s32 s32;
typedef __u32 u32;
typedef __s64 s64;
typedef __u64 u64;

#define __uint(name, val) int (*name)[val]
#define __type(name, val) typeof(val) *name
#define __array(name, val) typeof(val) *name[]
```
```c
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(u32));
    __uint(value_size, sizeof(u32));
} output SEC(".maps");
```

다음 BTF 4,5,6,7를 살펴 보자. 
```
[4] STRUCT 'user_msg_t' size=12 vlen=1
	'message' type_id=6 bits_offset=0
[5] INT 'char' size=1 bits_offset=0 nr_bits=8 encoding=SIGNED
[6] ARRAY '(anon)' type_id=5 index_type_id=7 nr_elems=12
[7] INT '__ARRAY_SIZE_TYPE__' size=4 bits_offset=0 nr_bits=32 encoding=(none)
```
* id 4는 user_msg_t struct 이고, 12바이트
*  그 struct에서 message는 id-6 번 타입이고
* id-5 에서는 C언어의 char타입에 대해서  1바이트로 정의한 내용이다. 
* id-6 은 배열이고 index 타입은 id-7에서 정의한다

```
[8] STRUCT '____btf_map_config' size=16 vlen=2
	'key' type_id=1 bits_offset=0
	'value' type_id=4 bits_offset=32
```
이것은 config라는 맵에 저장된 키-값 쌍에 대한 구조체 정의입니다.

나는 소스 코드에서 이 _btf_map_config 유형을 직접 정의하지 않았지만, 그것은 BCC에 의해 생성되었습니다. 키는 u32 형식이고 값은 user_msg_t 구조입니다. 이는 앞에서 본 유형 1과 4에 해당합니다.

이 구조에 대한 BTF 정보의 다른 중요한 부분은 값 필드가 구조체 시작 후 32비트에서 시작한다는 것입니다. 첫 32비트는 키 필드를 유지하는 데 필요하기 때문에 그것은 완전히 이치에 맞습니다.



### Maps with BTF information 

You’ve  just  seen  the  BTF  information  associated  with  a  map.  Now  let’s  see  how  this
BTF data is passed to the kernel when the map is created.

You  saw  in  Chapter  4  that  maps  are  created  using  the  bpf(BPF_MAP_CREATE)  syscall.
This takes a bpf_attr structure as a parameter, defined in the kernel like this (some
details omitted):

```c
	struct { /* anonymous struct used by BPF_MAP_CREATE command */
		__u32	map_type;	/* one of enum bpf_map_type */
		__u32	key_size;	/* size of key in bytes */
		__u32	value_size;	/* size of value in bytes */
		__u32	max_entries;	/* max number of entries in a map */
		__u32	map_flags;	/* BPF_MAP_CREATE related
					 * flags defined above.
					 */
		__u32	inner_map_fd;	/* fd pointing to the inner map */
		__u32	numa_node;	/* numa node (effective only if
					 * BPF_F_NUMA_NODE is set).
					 */
		char	map_name[BPF_OBJ_NAME_LEN];
		__u32	map_ifindex;	/* ifindex of netdev to create on */
		__u32	btf_fd;		/* fd pointing to a BTF type data */
		__u32	btf_key_type_id;	/* BTF type_id of the key */
		__u32	btf_value_type_id;	/* BTF type_id of the value */
		__u32	btf_vmlinux_value_type_id;/* BTF type_id of a kernel-
						   * struct stored as the
						   * map value
						   */
		/* Any per-map-type extra fields
		 *
		 * BPF_MAP_TYPE_BLOOM_FILTER - the lowest 4 bits indicate the
		 * number of hash functions (if 0, the bloom filter will default
		 * to using 5 hash functions).
		 */
		__u64	map_extra;
	};
```    

BTF가 도입되기 전에는 이 bpf_attr 구조에 btf_* 필드가 존재하지 않았으며 커널은 키 또는 값의 구조에 대해 알지 못했다.

key_size 및 value_size 필드는 메모리가 얼마나 필요한지 정의했지만 많은 바이트로 처리되었다. 키와 값의 유형을 정의하는 BTF 정보를 추가로 전달하면 커널이 검사할 수 있고 bpftool과 같은 유틸리티는 앞서 논의한 것처럼 예쁘게 인쇄하기 위한 유형 정보를 검색할 수 있다. 그러나 키와 값에 대해 별도의 BTF 유형 _id가 전달된다는 점은 흥미롭다. 방금 보신 ____btf_map_config 구조는 맵 정의에 대해 커널에서 사용하지 않고 사용자 공간 측면에서 BCC에서 사용한다.




### BTF Data for Functions and Function Prototypes

지금까지는 이 예제 출력의 BTF 데이터가 데이터 유형과 관련이 있었지만 BTF 데이터에는 함수 및 함수 프로토타입에 대한 정보도 포함되어 있습니다. 다음은 hello 함수를 설명하는 동일한 BTF 데이터 청크에서 가져온 정보입니다.

[31] FUNC_PROTO '(anon)' ret_type_id=23 vlen=1

    'ctx' type_id=10
[32] FUNC 'hello' type_id=31 linkage=static

유형 32에서 hello라는 함수는 이전 줄에 정의된 형식을 갖는 것으로 정의됩니다. 함수 원형이며, ID 23의 값을 반환하고 vlen=1이라는 단일 매개변수(ctx[10])를 가져옵니다. 완전성을 위해 출력의 앞부분에 나오는 해당 유형의 정의를 여기에 제공합니다.

[10] PTR '(anon)' type_id=0

[23] INT 'int' size=4 bits_offset=0 nr_bits=32 encoding=SIGNED

유형 10은 기본 유형이 0인 익명의 포인터이며, 명시적으로 BTF 출력에 포함되지 않지만 void 포인터로 정의됩니다.

리턴 값이 23유형인 4바이트 정수이고 encoding=SIGNED은 부호가 있는 정수임을 나타냅니다. 즉 양수 또는 음수 값을 가질 수 있습니다. 이는 hello-buffer-config.py의 소스 코드에서 함수 정의와 일치합니다. 다음과 같이 표시됩니다.

int hello(void *ctx)

이제까지 보여드린 예시 BTF 정보는 BTF 데이터 청크의 내용을 나열한 것입니다. 특정 맵 또는 프로그램과 관련된 BTF 정보만 얻는 방법을 알아보겠습니다



### Inspecting BTF Data for Maps and Programs

특정 맵과 관련된 BTF 형식을 검사하려면 bpftool이 쉽게 처리할 수 있습니다. 예를 들어 config 맵의 출력은 다음과 같습니다.

```
# bpftool btf dump map name config

[1] TYPEDEF 'u32' type_id=2

[4] STRUCT 'user_msg_t' size=12 vlen=1
    'essage' type_id=6 bits_offset=0
```    
마찬가지로 `# bpftool btf dump prog <prog identity>`를 사용하여 특정 프로그램과 관련된 BTF 정보를 검사할 수 있습니다. 


이 단계에서는 BTF가 데이터 구조와 함수의 형식을 어떻게 설명하는지 이해해야 합니다. C로 작성된 eBPF 프로그램에는 유형 및 구조를 정의하는 헤더 파일이 필요합니다. eBPF 프로그램에서 필요할 수 있는 커널 데이터 유형에 대한 헤더 파일을 생성하는 것이 얼마나 쉬운지 알아보겠습니다.


## Generating a Kernel Header File 
If you run bpftool btf list on a BTF-enabled kernel, you’ll see lots of preexisting blobs of BTF data that look like this:
```ksh
$ bpftool btf list
1: name [vmlinux]  size 5842973B
2: name [aes_ce_cipher]  size 407B
3: name [cryptd]  size 3372B
...
```
목록의 첫 번째 항목은 ID가 1이고 이름이 vmlinux인 BTF 정보입니다. 이(가상) 머신에서 실행 중인 커널에서 사용하는 모든 데이터 형식, 구조 및 함수 정의에 대한 정보입니다

eBPF 프로그램은 참조할 커널 데이터 구조 및 유형에 대한 정의가 필요합니다. CO-RE 이전에는 일반적으로 Linux 커널 소스의 많은 개별 헤더 파일 중 어떤 파일이 관심 있는 구조에 대한 정의를 가지고 있는지 알아내야 했지만 이제는 훨씬 더 쉬운 방법이 있습니다. BTF 사용 도구는 커널에 포함된 BTF 정보에서 적절한 헤더 파일을 생성할 수 있습니다.

이 헤더 파일은 일반적으로 vmlinux.h라고 하며 bpftool을 사용하여 다음과 같이 생성할 수 있습니다.

```log
# bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
```
이 파일에는 커널의 모든 데이터 유형이 정의되어 있으므로 생성한 vmlinux.h 파일을 eBPF 프로그램 소스 코드에 포함하면 필요한 모든 Linux 데이터 구조의 정의를 제공합니다. 소스를 eBPF 개체 파일로 컴파일할 때 해당 개체는 이 헤더 파일에서 사용된 정의와 일치하는 BTF 정보를 포함합니다. 나중에 프로그램이 대상 시스템에서 실행될 때 커널에 로드하는 사용자 공간 프로그램은 이 빌드 시간 BTF 정보와 대상 시스템에서 실행 중인 커널의 BTF 정보 간의 차이점을 설명하기 위해 조정을 수행합니다.

/sys/kernel/btf/vmlinux 파일 형식의 BTF 정보는 버전 5.4부터 Linux 커널에 포함되었지만 이전 커널에서도 사용할 수 있는 원시 BTF 데이터를 libbpf에서 생성할 수 있습니다. 다시 말해, 대상 시스템에 이미 BTF 정보가 없는 CO-RE 지원 eBPF 프로그램을 실행하려면 해당 대상에 대한 BTF 데이터를 직접 제공할 수 있습니다. BTFHub에서 BTF 파일을 생성하는 방법과 다양한 Linux 배포판에 대한 아카이브에 대한 정보를 찾을 수 있습니다.

BTFHub 저장소에는 CO-RE를 사용하여 커널 간에 이식할 수 있는 eBPF 프로그램을 작성하는 방법에 대한 추가 자료도 포함되어 있습니다. 내부.

다음으로 이러한 방법과 다른 전략을 사용하여 CO-RE를 사용하여 커널 간에 이식할 수 있는 eBPF 프로그램을 작성하는 방법을 살펴보겠습니다.



## CO-RE eBPF Programs

[bcc to libbpf 전환가이드](https://nakryiko.com/posts/bcc-to-libbpf-howto-guide/#bpf-code-conversion)


eBPF 프로그램이 커널에서 실행되는 것을 기억하실 것입니다. 이 장의 뒷부분에서 커널에서 실행되는 코드와 상호 작용할 사용자 공간 코드를 몇 가지 보여 주겠지만 이 섹션에서는 커널 쪽에 초점을 맞추고 있습니다.

앞에서 보았듯이 eBPF 프로그램은 eBPF 바이트코드로 컴파일되며(적어도 이 글을 쓰는 시점에서는) 이를 지원하는 컴파일러는 C 코드를 컴파일하기 위한 Clang 또는 gcc와 Rust 컴파일러입니다. 10장에서는 Rust를 사용하는 방법에 대해 몇 가지 설명하겠지만 이 장의 목적상 C를 작성하고 Clang 및 libbpf 라이브러리를 사용한다고 가정하겠습니다.

이 장의 나머지 부분에서는 hello-buffer-config이라는 예제 애플리케이션을 고려해 보겠습니다. BCC 프레임워크를 사용한 이전 장의 hello-buffer-config.py 예제와 매우 유사하지만 이 버전은 C로 작성되어 libbpf 및 CO-RE를 사용합니다.

BCC 기반 eBPF 코드를 libbpf로 마이그레이션하려는 경우 Andrii Nakryiko의 웹사이트에서 제공하는 훌륭하고 포괄적인 가이드를 확인하세요. BCC는 libbpf를 사용하는 것과 동일한 방식으로 처리되지 않는 몇 가지 편리한 바로 가기를 제공합니다. 반대로 libbpf는 eBPF 프로그래머가 더 쉽게 작업할 수 있도록 자체 매크로 및 라이브러리 함수 세트를 제공합니다. 예제를 살펴볼 때 BCC와 libbpf 접근 방식 간의 몇 가지 차이점을 지적하겠습니다.



### Header Files 

* 커널 헤더파일 
* libbpf 라이브러리 헤더파일
* 사용자 정의 헤더 파일

The first few lines of hello-buffer-config.bpf.c specify the header files that it needs:

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "hello-buffer-config.h"
```
These  five  files  are  the  vmlinux.h  file,  a  few  headers  from  libbpf,  and  an  application-specific  header  file  that  I  wrote  myself.  Let’s  see  why  this  is  a  typical  pattern  for  the header files needed for a libbpf program.


#### 1. kernel header information
커널 데이터 구조 또는 유형을 참조하는 eBPF 프로그램을 작성하는 경우 가장 쉬운 옵션은 이 장의 앞부분에서 설명한 vmlinux.h 파일을 포함하는 것입니다.

대안으로 Linux 소스에서 개별 헤더 파일을 포함하거나 이러한 번거로움을 원하는 경우 자신의 코드에서 수동으로 유형을 정의할 수 있습니다.

libbpf에서 BPF 도우미 함수를 사용하려는 경우 BPF 도우미 소스에서 참조하는 u32, u64 등의 유형에 대한 정의를 얻으려면 vmlinux.h 또는 linux/types.h를 포함해야 합니다.

vmlinux.h 파일은 커널 소스 헤더에서 파생되지만 #define'd 값은 포함하지 않습니다. 예를 들어 eBPF 프로그램이 이더넷 패킷을 구문 분석하는 경우 패킷에 포함된 프로토콜을 알려주는 상수 정의(예: IP 패킷임을 나타내는 0x0800 또는 ARP 패킷의 경우 0x0806)가 필요할 것입니다. 커널에 이러한 값을 정의하는 if_ether.h 파일을 포함하지 않는 경우 자체 코드에서 중복해야 하는 일련의 상수 값이 있습니다. hello-buffer-config에 이러한 값 정의가 필요하지 않았지만 이와 관련된 다른 예가 8장에 나와 있습니다.


#### 2. Headers from libbpf
eBPF 코드에서 BPF 도우미 함수를 사용하려면 해당 정의를 제공하는 libbpf에서 헤더 파일을 포함해야 합니다.

libbpf에 대해 약간 혼란스러울 수 있는 한 가지는 사용자 공간 라이브러리가 아니라는 것입니다. 사용자 공간과 eBPF C 코드 모두에서 libbpf에서 헤더 파일을 포함하는 자신을 발견하게 될 것입니다.

이 글을 쓸 당시 eBPF 프로젝트가 libbpf를 서브모듈로 포함하고 소스에서 빌드/설치하는 것을 흔히 볼 수 있습니다. 이 책의 예제 저장소에서 내가 한 일입니다. 서브모듈로 포함하면 libbpf/src 디렉토리에서 make install을 실행하기만 하면 됩니다. libbpf가 일반적인 Linux 배포판의 패키지로 널리 사용되는 것을 보는 데 그리 오래 걸리지 않을 것이라고 생각합니다. 특히 libbpf가 버전 1.0 릴리스의 마일스톤을 통과했기 때문입니다. 


#### 3. Application-specific header 
애플리케이션의 사용자 공간과 eBPF 부분 모두에서 사용하는 모든 구조를 정의하는 애플리케이션별 헤더 파일이 매우 일반적입니다. 내 예제에서 hello-buffer-config.h 헤더 파일은 eBPF 프로그램에서 사용자 공간으로 이벤트 데이터를 전달하는 데 사용하는 data_t 구조를 정의합니다. BCC 버전의 코드와 거의 동일하며 다음과 같습니다.

이전에 본 버전과 유일한 차이점은 path라는 필드를 추가한 것입니다.

이 구조 정의를 별도의 헤더 파일로 가져오는 이유는 hello-buffer-config.c의 사용자 공간 코드에서도 참조하기 위함입니다. BCC 버전에서 커널과 사용자 공간 코드는 모두 하나의 파일에 정의되었으며 BCC는 일부 작업을 수행하여 해당 구조를 Python 사용자 공간 코드에 사용할 수 있도록 했습니다.

### Defining Maps
Map을 어떻게 정의하느냐 하면 ..
* BCC에서는 정말 편리하게 마크로를 이용해서  `BPF_HASH(config, u64, struct user_msg_t);` 이렇게 정의 했는데 여기서는 좀더 명확하게 구체적으로 정의를 해줘야 한다는 것이다. 
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
```

* bpf/bpf_helpers_def.h 

This macro isn’t available when you’re not using BCC, so in C you have to write it out longhand.  You’ll  see  that  I  have  used  __uint  and  __type.  These  are  defined  in  bpf/bpf_helpers_def.h along with __array, like this

```c
#define __uint(name, val) int (*name)[val]
#define __type(name, val) typeof(val) *name
#define __array(name, val) typeof(val) *name[]
```


### eEPF program sections

libbpf를 사용하면 각 eBPF 프로그램에 프로그램 유형을 정의하는 SEC() 매크로를 표시해야 합니다.

* SEC("kprobe")

이렇게 하면 컴파일된 ELF 개체에 kprobe라는 섹션이 생성되어 libbpf가 이를 BPF_PROG_TYPE_KPROBE로 로드하도록 인식합니다. 7장에서 다양한 프로그램 유형에 대해 자세히 설명하겠습니다.

프로그램 유형에 따라 섹션 이름을 사용하여 프로그램이 연결된 이벤트를 지정할 수도 있습니다. libbpf 라이브러리는 이 정보를 사용하여 사용자 공간 코드에서 명시적으로 설정하는 대신 연결을 자동으로 설정합니다. 예를 들어 ARM 기반 시스템의 execve 시스템 호출에 대한 kprobe에 자동으로 연결하려면 다음과 같이 섹션을 지정할 수 있습니다.

* SEC("kprobe/__arm64_sys_execve")

이렇게 하려면 해당 아키텍처의 시스템 호출에 대한 함수 이름을 알아야 합니다(또는 대상 시스템의 /proc/kallsyms 파일을 확인하여 알아낼 수 있습니다. 여기에는 커널 기호(함수 이름 포함)가 모두 나열되어 있습니다). 그러나 libbpf는 로드에게 아키텍처별 함수에서 자동으로 kprobe에 연결하도록 지시하는 k(ret)syscall 섹션 이름으로 생활을 더욱 편리하게 할 수 있습니다.

* SEC("ksyscall/execve")

좀 아키텍처의 시스템 호출함수를 알려면 좀 복잡하니까... 
python에서 이렇게 참조할 수 있도록 했던 것처럼 해주는 macro를제공한다는 뜻이군요 .

```py
syscall = b.get_syscall_fnname("execve")
```

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
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), p->message);
   } else {
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), message); 
   }

   bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, &data, sizeof(data));   
   return 0;
}
```
1. libbpf에서 정의한 BPF_KPROBE_SYSCALL 매크로를 사용하여 시스템 호출 인수에 쉽게 액세스할 수 있습니다. execve()의 경우 첫 번째 인수인 실행할 프로그램의 경로 이름이 있습니다. eBPF 프로그램 이름은 hello입니다.

2. 매크로를 사용하여 execve()에 대한 경로 이름 인수에 액세스하기가 매우 쉬우므로 perf 버퍼 출력에 전송되는 데이터에 포함합니다. 메모리를 복사하려면 BPF 도우미 함수를 사용해야 합니다. 

3. 여기서 bpf_map_lookup_elem()은 맵에서 값을 조회하기 위한 BPF 도우미 함수입니다. 맵에서 주어진 키를 사용하여 BCC의 이와 유사한 동등한 것은 p = my_con fig.lookup(&data.uid)입니다. BCC는 C 코드를 컴파일러로 전달하기 전에 이 함수를 기본 bpf_map_lookup_elem() 함수로 다시 작성합니다. libbpf를 사용할 때 컴파일하기 전에 코드를 다시 작성할 수 없으므로 도우미 함수에 직접 작성해야 합니다.

4. 다음은 비슷한 예로, BCC가 편리한 출력.perf_submit(ctx, &data, sizeof(data))와 동일한 도우미 함수 bpf_perf_event_output()에 직접 작성한 것입니다.


다른 차이점은 BCC 버전에서 message 문자열을 hello() 함수 내에서 지역 변수로 정의했다는 것입니다. BCC는(적어도 이 글을 쓸 당시에는) 전역 변수를 지원하지 않습니다. 이 버전에서는 다음과 같이 전역 변수로 정의했습니다.

```c
char message[12] = "Hello World";
````

BPF_KPROBE_SYSCALL 매크로는 언급한 libbpf의 편리한 추가 기능 중 하나입니다. 매크로를 사용해야 하는 것은 아니지만 사용하면 편리합니다. 시스템 호출에 전달된 모든 매개변수에 대해 명명된 인수를 제공하려면 무거운 작업을 수행합니다. 이 경우 실행될 실행 파일의 경로를 포함하는 문자열을 가리키는 경로 이름 인수를 제공합니다. execve() 시스템 호출의 첫 번째 인수입니다.


매우 주의 깊게 살펴보면 ctx 변수가 hello-buffer-config.bpf.c의 소스 코드에서 명확하게 정의되지 않았음을 알 수 있지만 그럼에도 불구하고 다음과 같이 출력 perf 버퍼에 데이터를 제출할 때 사용할 수 있었습니다.
```c
bpf_perf_event_output(ctx, &output, BPF_F_CURRENT_CPU, &data, sizeof(data))
```

ctx 변수는 bpf/bpf_tracing.h 내부의 BPF_KPROBE_SYSCALL 매크로 정의 내에 숨겨져 있으며 libbpf에 있으며 이에 대한 설명도 찾을 수 있습니다. 변수가 보이지 않게 정의되어 있지만 액세스할 수 있다는 것은 약간 혼란스러울 수 있습니다.



### Memory Access with CO-RE
아래와 같은 함수에서 커널 데이터를 참조해야 하는 경우.. bpf_probe_read_() 계열의 helper 함수를 사용한다. 
```c
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), p->message);   
      bpf_probe_read_kernel_str(&data.message, sizeof(data.message), message);
```

추적용 eBPF 프로그램은 bpf_probe_read_*() 계열의 BPF 도우미 함수를 통해 메모리 액세스가 제한됩니다. bpf_probe_write_user() 도우미 함수도 있지만 "실험용"일 뿐입니다. 문제는 다음 장에서 보겠지만 eBPF 검증자는 일반적으로 C에서 일반적으로 할 수 있는 것처럼 포인터를 통해 메모리를 읽도록 허용하지 않는다는 것입니다.

libbpf 라이브러리는 bpf_probe_read_*() 도우미를 통해 CO-RE 래퍼를 제공하여 BTF 정보를 활용하고 메모리 액세스 호출을 다른 커널 버전에 걸쳐 휴대 가능하게 만듭니다. 다음은 bpf_core_read.h 헤더 파일에 정의된 래퍼 중 하나의 예입니다.
```c
#define bpf_core_read(dst, sz, src) \
bpf_probe_read_kernel(dst, sz, (const void *)__builtin_preserve_access_index(src))
```                          
보시다시피 bpf_core_read()은 bpf_probe_read_kernel()에 직접 호출합니다. 유일한 차이점은 __builtin_preserve_access_index()로 src 필드를 감싸는 것입니다. 이렇게 하면 Clang에서 CO-RE 재배치 항목을 생성하고 메모리에서 이 주소를 액세스하는 eBPF 명령어를 생성합니다.

이 장 뒷부분에서 볼 수 있듯이 CO-RE 재배치 항목은 eBPF 프로그램을 커널로 로드할 때 libbpf에 주소를 다시 작성하도록 지시하여 BTF 차이를 고려합니다. 대상 커널에서 src의 오프셋이 다르면 다시 작성된 명령어는 이를 고려합니다.

libbpf 라이브러리는 BPF_CORE_READ() 매크로를 제공하여 여러 개의 bpf_core_read() 호출을 단일 행에 작성할 수 있습니다. 매크로를 사용하면 모든 포인터 역참조를 위해 별도의 도우미 함수 호출이 필요하지 않습니다. 예를 들어 d = a->b->c->d와 같은 작업을 수행하려면 다음 코드를 작성할 수 있습니다


```c
struct b_t *b;
struct c_t *c;
bpf_core_read(&b, 8, &a->b);
bpf_core_read(&c, 8, &b->c);
bpf_core_read(&d, 8, &c->d);
```

좀 더 간단하게...

```c
d = BPF_CORE_READ(a, b, c, d);
```
#### BPF_CORE_READ 

BCC는 BPF 코드를 자동으로 다시 작성하고 필드 액세스를 tsk->parent->pid일련의 bpf_probe_read()호출로 전환합니다. Libbpf/BPF CO-RE에는 이러한 고급 기능이 없지만 bpf_core_read.h바닐라 C에서 가능한 한 이에 가까워질 수 있도록 도우미 세트를 제공합니다. 위의 tsk->parent->pid 내용이 됩니다

BPF_CORE_READ(tsk, parent, pid). tp_btfLinux 5.5부터 사용 가능한 및 fentry/ BPF 프로그램 유형을 사용하면 fexit자연스러운 C 구문도 가능합니다. 그러나 이전 커널 및 기타 BPF 프로그램 유형(예: 추적점 및 kprobe)의 경우 가장 좋은 방법은 BPF_CORE_READ.

또한 BPF_CORE_READ매크로는 BCC 모드에서도 작동하므로 #ifdef __BCC__/ #else/ 를 사용한 모든 필드 액세스의 중복을 피하기 위해 #endif모든 필드 읽기를 BPF_CORE_READBCC 및 libbpf 모드 모두로 변환할 수 있습니다. 하지만 BCC를 사용하면 헤더가 최종 BPF 프로그램의 일부인지 확인하세요 bpf_core_read.h.

### License Definition 
As  you  already  know  from  Chapter  3,  the  eBPF  program  has  to  declare  its  license.
The example code does it like this:
```
char LICENSE[] SEC("license") = "Dual BSD/GPL";
```
You’ve  now  seen  all  the  code  in  the  hello-buffer-config.bpf.c  example.  Now  let’s  com‐
pile it into an object file



## Compiling eBPF programs for CO-RE


### Debuf information
Clang에 -g 플래그를 전달하여 디버그 정보에 필요한 BTF를 포함해야 합니다. 그러나 -g 플래그는 또한 출력 개체 파일에 DWARF 디버깅 정보를 추가하지만 eBPF 프로그램에서는 필요하지 않으므로 다음을 실행하여 개체 크기를 줄일 수 있습니다.

llvm-strip -g <object file>


### Optimixation
-O2 최적화 플래그(레벨 2 이상)는 Clang이 검증기를 통과할 BPF 바이트코드를 생성하기 위해 필요합니다. 이것이 필요한 한 가지 예는 기본적으로 Clang이 헬퍼 함수를 호출하기 위해 callx <register>를 출력한다는 것입니다. 그러나 eBPF는 레지스터에서 주소를 호출하는 것을 지원하지 않습니다.


### Target Architecture
특정 libbpf에서 정의한 매크로를 사용하는 경우 컴파일 시간에 대상 아키텍처를 지정해야 합니다. 
libbpf 헤더 파일 bpf/bpf_tracing.h는 BPF_KPROBE 및 BPF_KPROBE_SYSCALL과 같은 플랫폼 전용으로 정의됩니다. 
이 예에서 사용한 매크로. BPF_KPROBE 매크로를 kprobe에 연결하는 eBPF 프로그램에 사용할 수 있으며 BPF_KPROBE_SYSCALL은 syscall kprobe에 대한 변형입니다.

kprobe의 인수는 CPU 레지스터의 내용 사본을 저장하는 pt_regs 구조입니다. 레지스터는 아키텍처별이므로 pt_regs 구조 정의는 실행 중인 아키텍처에 따라 달라집니다.. 이러한 매크로를 사용하려면 대상 아키텍처가 무엇인지 컴파일러에도 알려야 합니다. $ARCH가 arm64, amd64 등과 같은 아키텍처 이름과 같은 경우 -D _TARGET_ARCH($ARCH)를 설정하여 이렇게 할 수 있습니다.

매크로를 사용하지 않으면 kprobe를 위해 레지스터 정보에 대한 아키텍처별 코드가 필요합니다.

아마도 "아키텍처당 한 번 컴파일하고 어디에서나 실행"은 약간 복잡했을 것입니다!



### Makefile 
다음은 CO-RE 객체(이 책의 GitHub 리포지토리의 chapter5 디렉토리에 있는 Makefile에서 가져온)를 컴파일하기 위한 Makefile 지시어의 예입니다.
```
hello-buffer-config.bpf.o: %.o: %.c

clang \

   -target bpf \
   -D __TARGET_ARCH_$(ARCH) \
   -I/usr/include/$(shell uname -m)-linux-gnu \
   -Wall \
   -O2 -g \
   -c $< -o $@
llvm-strip -g $@
```
예제 코드를 사용하는 경우 chapter5 디렉토리에서 make를 실행하여 hello-buffer-config.bpf.o eBPF 개체 파일을 빌드할 수 있어야 합니다. (그리고 곧 설명할 사용자 공간 실행 파일). 개체 파일에 BTF 정보가 포함되어 있는지 확인해 봅시다.



### BTF information in the Object file
BTF에 대한 커널 문서에서는 BTF 데이터가 ELF 개체 파일에 어떻게 인코딩되는지 설명하고 있습니다. 데이터와 문자열 정보를 포함하는.BTF와 함수와 선 정보를 다루는.BTF.ext의 두 섹션으로 나뉩니다. readelf를 사용하여 이러한 섹션이 개체 파일에 추가되었는지 확인할 수 있습니다.
```
$ readelf -S hello-buffer-config.bpf.o | grep BTF
[10].BTF PROGBITS 0000000000000000 000002c0
[11].rel.BTF REL 0000000000000000 00000e50
[12].BTF.ext PROGBITS 0000000000000000 00000b18
[13].rel.BTF.ext REL 0000000000000000 00000ea0
```
bpftool 유틸리티를 사용하면 다음과 같이 개체 파일에서 BTF 데이터를 검사할 수 있습니다.
```
bpftool btf dump file hello-buffer-config.bpf.o
```
출력은 이 장의 앞부분에서 살펴본 것처럼 로드된 프로그램 및 맵에서 BTF 정보를 덤프할 때 얻는 출력과 비슷합니다.

BTF 정보가 프로그램을 다른 커널 버전과 다른 데이터 구조로 실행할 수 있도록 하는 데 어떻게 사용될 수 있는지 알아봅시다.




## BPF Relocation
libbpf 라이브러리는 eBPF 프로그램을 적용하여 실행되는 대상 커널의 데이터 구조 레이아웃과 함께 작동합니다. 레이아웃이 코드를 컴파일한 커널과 다른 경우에도 마찬가지입니다. 이를 위해 libbpf는 컴파일 프로세스의 일부로 Clang에 의해 생성된 BPF CO-RE 재배치 정보가 필요합니다.

재배치가 작동하는 방식에 대한 자세한 내용은 linux/bpf.h 헤더 파일의 bpf_core_relo 구조체 정의에서 확인할 수 있습니다.

struct bpf_core_relo {

__u32 insn_off;
__u32 type_id;
__u32 access_str_off;
enum bpf_core_relo_kind kind;
};

eBPF 프로그램에 대한 CO-RE 재배치 데이터는 재배치가 필요한 각 명령어에 대해 이러한 구조 중 하나로 구성됩니다. 
* 명령어가 레지스터를 구조체 내의 필드 값으로 설정한다고 가정해 봅시다. 
* 해당 명령어에 대한 bpf_core_relo 구조(insn_off 필드로 식별됨)는 해당 구조체의 BTF 유형(type_id 필드)을 인코딩하고 해당 필드가 해당 구조에 상대적으로 액세스되는 방식도 표시합니다.



앞서 보았듯이 커널 데이터 구조에 대한 재배치 데이터는 Clang에 의해 자동으로 생성되고 ELF 개체 파일에 인코딩됩니다. vmlinux.h 파일의 시작 부분에 다음 줄이 있으면 Clang에서 이렇게 할 수 있습니다.

#pragma clang attribute push (__attribute__((preserve_access_index)), apply_to = record)

* preserve_access_index 속성은 Clang에 BPF CO-RE 재배치를 생성하도록 지시합니다. 
* clang 속성 push 부분은 이 속성이 파일에 나타나는 clang 속성 pop까지 모든 정의에 적용되어야 한다고 말합니다. 파일의 끝. 즉 Clang은 vmlinux.h에 정의된 모든 유형에 대한 재배치 정보를 생성합니다.

bpftool을 사용하여 프로그램을 로드할 때 다음과 같이 -d 플래그로 디버그 정보를 켜면 재배치 과정을 볼 수 있습니다.

```
# bpftool -d prog load hello.bpf.o /sys/fs/bpf/hello
```

이렇게 하면 많은 출력이 생성되지만 재배치와 관련된 부분은 다음과 같습니다.
```
libbpf: CO-RE relocating [24] struct user_pt_regs: found target candidate [205]
struct user_pt_regs in [vmlinux]
libbpf: prog 'hello': relo #0: <byte_off> [24] struct user_pt_regs.regs[0]
(0:0:0 @ offset 0)
libbpf: prog 'hello': relo #0: matching candidate #0 <byte_off> [205] struct
user_pt_regs.regs[0] (0:0:0 @ offset 0)
libbpf: prog 'hello': relo #0: patched insn #1 (LDX/ST/STX) off 0 -> 
```
이 예에서 hello 프로그램의 BTF 정보에서 유형 ID 24는 user_pt_regs라는 구조를 나타냄을 알 수 있습니다. libbpf 라이브러리는 이를 vmlinux BTF 데이터 세트에서 유형 ID 205인 user_pt_regs라는 커널 구조와 일치시켰습니다. 실제로는 프로그램을 컴파일하고 동일한 시스템에 로드했기 때문에 유형 정의가 동일하므로 이 예에서 구조의 시작 부분에서 오프셋 0은 변경되지 않고 유지되며 명령어 #1에 대한 "패치"도 변경되지 않은 상태로 유지됩니다.

많은 애플리케이션에서 사용자에게 bpftool을 실행하여 eBPF 프로그램을 로드하도록 요청하고 싶지 않을 것입니다. 대신 사용자 공간에 이 기능을 내장하여 제공하는 전용 사용자 공간 프로그램으로 구축하려고 할 것입니다. 실행 가능. 사용자 공간 코드를 작성하는 방법에 대해 고려해 보겠습니다.

## CO-RE user space code
eBPF 프로그램을 커널로 로드할 때 재배치를 구현하여 CO-RE를 지원하는 여러 프로그래밍 언어로 작성된 몇 가지 프레임워크가 있습니다. 이 장에서는 libbpf를 사용하는 C 코드를 보여주고 다른 옵션으로는 Go 패키지 cilium/ebpf 및 libbpfgo, Rust용 Aya 등이 있습니다.

* 재배치 가능한 프로그램을 user code에서 어떻게 배치시켜줄지에 대한 것이 좀 어렵기 때문에 이것을 지원하는 것이 bcc 같은 것이 있고, 그런데 이것은 CO-RE 개념을 지원하지 않기 때문에 즉 실행환경에서 매번 컴파일을 해야 하는 것이기 때문에  이런 단점을 보완하려고 CO-RE 방식, 재배치 가능한 방식으로 컴파일하는 프레임워크가 제공된다. 
* 그 중에서 C 언어기반에서는 BPF skeleton 이 있다. 
* go 언어 기반 framework 도 있다. 

## The libbpf library for user space
libbpf 라이브러리는 C에서 사용자 공간 부분을 작성하는 경우 직접 사용할 수 있는 사용자 공간 라이브러리입니다. 원한다면 CO-RE를 사용하지 않고 이 라이브러리를 사용할 수 있습니다. Andrii Nakryiko의 훌륭한 블로그 게시물 libbpf-bootstrap에 이에 대한 예가 있습니다.

이 라이브러리는 4장에서 소개한 bpf() 및 관련 시스템 호출을 래핑하는 함수를 제공하여 프로그램을 커널에 로드하고 이벤트에 연결하는 등의 작업을 수행하거나 사용자 공간에서 맵 정보에 액세스할 수 있습니다. 이러한 추상화를 사용하는 가장 쉽고 일반적인 방법은 자동 생성된 BPF 스켈레톤 코드를 통해 이루어집니다.

### BPF Skeletons
bpftool을 사용하여 ELF 파일 형식의 기존 eBPF 개체에서 이 스켈레톤 코드를 자동 생성할 수 있습니다. 이렇게 하려면 다음과 같이 하십시오.

```
# bpftool gen skeleton hello-buffer-config.bpf.o > hello-buffer-config.skel.h
```
이 스켈레톤 헤더를 살펴보면 eBPF 프로그램 및 맵에 대한 구조 정의를 포함하고 있음을 알 수 있습니다. hello_buffer_config_bpf__라는 이름으로 시작하는 여러 함수(개체 파일의 이름에 기반). 이러한 함수는 eBPF 프로그램 및 맵의 수명 주기를 관리합니다. 스켈레톤 코드를 사용할 필요가 없습니다. 직접 libbpf에 전화를 걸 수 있습니다. 선호한다면 - 그러나 자동 생성된 코드는 일반적으로 일부 타이핑을 절약해 줍니다.

생성된 스켈레톤 파일의 끝부분에 hello_buffer_config_bpf__elf_bytes라는 함수가 있습니다. hello-buffer-config.bpf.o. 스켈레톤이 생성되면 해당 개체 파일이 더 이상 필요하지 않습니다. make를 실행하여 hello-buffer-config 실행 파일을 생성한 다음.o 파일을 삭제하여 이를 테스트할 수 있습니다. 실행 파일에는 eBPF 바이트코드가 포함되어 있습니다.


```c
... [other #includes]
#include "hello-buffer-config.h"                                       
#include "hello-buffer-config.skel.h"
... [some callback functions]
int main()
{
   struct hello_buffer_config_bpf *skel;
   struct perf_buffer *pb = NULL;
   int err;
   libbpf_set_print(libbpf_print_fn);                                 
   skel = hello_buffer_config_bpf__open_and_load();                   
...
   err = hello_buffer_config_bpf__attach(skel);                       
...
   pb = perf_buffer__new(bpf_map__fd(skel->maps.output), 8, handle_event,
                                                         lost_event, NULL, NULL);                                              
                                                                      
...
   while (true) {                                                     
       err = perf_buffer__poll(pb, 100);
...}
   perf_buffer__free(pb);                                             
   hello_buffer_config_bpf__destroy(skel);
   return -err;
}
```

1. 이 파일에는 자동으로 생성된 스켈레톤 헤더와 사용자 공간과 커널 간에 공유되는 데이터 구조에 대해 수동으로 작성한 헤더 파일이 포함됩니다.
2. 이 코드는 libbpf에서 생성된 로그 메시지를 인쇄할 콜백 함수를 설정합니다.
3. ELF 바이트에 정의된 모든 맵과 프로그램을 나타내는 골격 구조가 생성되고 커널에 로드됩니다.
4. 프로그램이 적절한 이벤트에 자동으로 연결됩니다.
5. 이 함수는 perf 버퍼 출력을 처리하기 위한 구조를 만듭니다.
6. 여기서 perf 버퍼가 지속적으로 폴링됩니다.
7. 이것은 정리 코드입니다

#### Loading programs and maps into the kernel

자동 생성된 함수에 대한 첫 번째 호출은 다음과 같습니다.
```
skel = hello_buffer_config_bpf__open_and_load();
```
이름에서 알 수 있듯이 이 함수는 열기 및 로드라는 두 단계를 다룹니다. "열기" 단계에서는 ELF 데이터를 읽고 해당 섹션을 eBPF 프로그램 및 맵을 나타내는 구조로 변환합니다. "로드" 단계에서는 필요한 경우 CO-RE 수정 작업을 수행하면서 이러한 맵과 프로그램을 커널에 로드합니다.
이러한 두 단계는 골격 코드가 별도의 이름__open() 및 이름__load() 함수를 제공하므로 쉽게 분리 처리할 수 있습니다. 이렇게 하면 로드하기 전에 eBPF 정보를 조작할 수 있는 옵션이 제공됩니다. 로드하기 전에 프로그램을 구성하는 것이 일반적입니다. 예를 들어 전역 카운터 변수 c를 초기화할 수 있습니다.
다음과 같이 10과 같은 일부 값으로.

```
skel = hello_buffer_config_bpf__open();
if (!skel) {
    // 오류...
}   
skel->data->c = 10;
err = hello_buffer_config_bpf__load(skel);
```
hello_buffer_config_bpf__open()에 의해 반환된 데이터 형식은 다음과 같습니다. hello_buffer_config_bpf__load()에 의해 반환된 데이터 형식도 골격 헤더에서 정의된 hello_buffer_config_bpf라는 구조로, 개체 파일에 정의된 모든 맵, 프로그램 및 데이터에 대한 정보를 포함합니다.

#### Accessing existing maps
기본적으로 libbpf는 ELF 바이트에 정의된 맵도 만들지만 때로는 기존 맵을 재사용하는 eBPF 프로그램을 작성하려는 경우도 있습니다.

이전 장에서 bpftool을 통해 모든 맵을 반복하면서 지정된 이름에 일치하는 맵을 찾는 예제를 이미 보았습니다.

다른 공통적인 이유로 맵을 사용하는 것은 두 개의 서로 다른 eBPF 프로그램 간에 정보를 공유하기 위해 하나의 프로그램만 맵을 만들어야 합니다.

bpf_map__set_autocreate() 함수를 사용하면 libbpf의 자동 생성을 재정의할 수 있습니다.

* 어떻게 기존에 있는 map를 찾는 방법


기존 맵에 어떻게 액세스합니까? 맵은 고정될 수 있으며 고정 경로를 알고 있으면 bpf_obj_get()을 사용하여 기존 맵에 대한 파일 설명자를 가져올 수 있습니다. 다음은 매우 간단한 예입니다(GitHub 저장소에서 chapter5/find-map.c로 사용 가능).

```c
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <bpf/bpf.h>

// Run this as root
int main()
{
    struct bpf_map_info info = {}; 
    unsigned int len = sizeof(info); 

    int findme = bpf_obj_get("/sys/fs/bpf/findme");
    if (findme <= 0) {
        printf("No FD\n");
    } else {
        bpf_obj_get_info_by_fd(findme, &info, &len);
        printf("name %s\n", info.name);
    }
}
```

다음과 같이 bpftool을 사용하여 맵을 만들 수 있습니다.
```c
$ bpftool map create /sys/fs/bpf/findme type array key 4 value 32 entries 4
name findme
```
find-map 실행 가능 파일을 실행하면 다음과 같이 출력됩니다.
이름: findme
hello-buffer-config 예제와 골격 코드로 돌아갑니다.

#### Attaching to events

예제의 다음 스켈레톤 함수는 프로그램을 execve 시스템 호출 함수에 연결합니다.

err = hello_buffer_config_bpf__attach(skel);
libbpf 라이브러리는 이 프로그램에 대한 SEC() 정의에서 자동으로 첨부 포인트를 가져옵니다. 연결 지점을 완전히 정의하지 않은 경우 bpf_program__attach_kprobe, bpf_program__attach_xdp 등과 같은 전체 일련의 libbpf 함수가 있습니다. 다양한 프로그램 유형 첨부하기.

#### Managing an event buffer
perf 버퍼를 설정하려면 skel이 아닌 libbpf 자체에 정의된 함수를 사용합니다.
```c
pb = perf_buffer__new(bpf_map__fd(skel->maps.output), 8, handle_event,lost_event, NULL, NULL);
```
perf_buffer__new() 함수는 첫 번째 인수로 "출력" 맵에 대한 파일 설명자를 가져오는 것을 볼 수 있습니다. handle_event 인자는 콜백 함수입니다. 새 데이터가 perf 버퍼에 도착할 때 호출되며, lost_event는 커널이 데이터 항목을 쓸 수 있는 perf 버퍼의 공간이 충분하지 않은 경우 호출됩니다. 내 예제에서는 이러한 함수가 화면에 메시지를 작성하기만 합니다.

Finally, the program has to poll the perf buffer repeatedly:
```c
while (true) {
   err = perf_buffer__poll(pb, 100);
   ...
}
```
The 100 is a timeout in milliseconds. The callback functions previously set up will get
called as appropriate when data arrives or when the buffer is full.
Finally, to clean up I free the perf buffer and destroy the eBPF programs and maps in
the kernel, like this:
```c
perf_buffer__free(pb);
hello_buffer_config_bpf__destroy(skel);
```
There  are  a  whole  set  of  perf_buffer_*-  and  ring_buffer_*-related  functions  in
libbpf to help you manage event buffers.
If you make and run this example hello-buffer-config program, you’ll see the fol‐
lowing output (that’s very similar to what you saw in Chapter 4):
```
23664  501    bash             Hello World
23665  501    bash             Hello World
23667  0      cron             Hello World
23668  0      sh               Hello Worl
```


### Libbpf code examples

libbpf를 기반으로 한 eBPF 프로그램의 훌륭한 예가 많이 있으므로 다음과 같이 사용할 수 있습니다.

• libbpf-bootstrap 프로젝트는 일련의 예제 프로그램을 통해 기반을 다지는 데 도움을 주기 위한 것입니다.
• BCC 프로젝트에는 원래 BCC 기반 도구 중 많은 도구가 libbpf로 마이그레이션되었습니다. 버전. libbpf-tools 디렉토리에서 찾을 수 있습니다.

## 요약
CO-RE를 사용하면 eBPF 프로그램을 빌드한 버전과 다른 커널 버전에서 실행할 수 있습니다. 버전. 이는 eBPF의 휴대성을 크게 향상시킵니다.

생산 준비가 완료된 툴링을 사용자와 고객에게 제공하려는 도구 개발자의 삶을 훨씬 쉽게 만듭니다.

이 장에서는 CO-RE가 유형 정보를 인코딩하여 이를 달성하는 방법을 알아보았습니다.

컴파일된 개체 파일에  커널로 로드됨에 따라 지시를 다시 작성하기 위한 재배치. 또한 C로 코드를 작성하는 방법에 대한 소개도 제공했습니다.

libbpf: 커널에서 실행되는 eBPF 프로그램과 사용자 공간 프로그램 자동 생성된 BPF 스켈레톤을 기반으로 이러한 프로그램의 수명주기를 관리하는 코드입니다


## 컴파일에러  
* 기존 vmlinux.h 파일을 가지고  make 하게되면 에러가 발생한다. 
* bcc/libbpf-tools/x86/vmlinu.h를 이쪽으로 현재 위치로 복사해서 사용한다. 

```sh
jhyunlee@Good:~/go/src/eBPF/ebpf-learning/LAB/lab5$ make
clang \
    -target bpf \
        -D __TARGET_ARCH_x86 \
    -Wall \
    -O2 -g -o hello-buffer-config.bpf.o -c hello-buffer-config.bpf.c
hello-buffer-config.bpf.c:27:5: error: no member named 'di' in 'struct pt_regs'
int BPF_KPROBE_SYSCALL(hello, const char *pathname)
    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/usr/include/bpf/bpf_tracing.h:561:28: note: expanded from macro 'BPF_KPROBE_SYSCALL'
#define BPF_KPROBE_SYSCALL BPF_KSYSCALL
                           ^
/usr/include/bpf/bpf_tracing.h:548:31: note: expanded from macro 'BPF_KSYSCALL'
                               ? (struct pt_regs *)PT_REGS_PARM1(ctx)       \
                                                   ^~~~~~~~~~~~~~~~~~
/usr/include/bpf/bpf_tracing.h:272:46: note: expanded from macro 'PT_REGS_PARM1'
#define PT_REGS_PARM1(x) (__PT_REGS_CAST(x)->__PT_PARM1_REG)
                          ~~~~~~~~~~~~~~~~~  ^
/usr/include/bpf/bpf_tracing.h:77:24: note: expanded from macro '__PT_PARM1_REG'
#define __PT_PARM1_REG di
                       ^
hello-buffer-config.bpf.c:27:5: error: no member named 'di' in 'struct pt_regs'
int BPF_KPROBE_SYSCALL(hello, const char *pathname)
    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/usr/include/bpf/bpf_tracing.h:561:28: note: expanded from macro 'BPF_KPROBE_SYSCALL'
#define BPF_KPROBE_SYSCALL BPF_KSYSCALL
                           ^
/usr/include/bpf/bpf_tracing.h:553:21: note: expanded from macro 'BPF_KSYSCALL'
                return ____##name(___bpf_syswrap_args(args));               \
                                  ^~~~~~~~~~~~~~~~~~~~~~~~~
/usr/include/bpf/bpf_tracing.h:514:42: note: expanded from macro '___bpf_syswrap_args'
#define ___bpf_syswrap_args(args...)     ___bpf_apply(___bpf_syswrap_args, ___bpf_narg(args))(args)
## CO-RE Overview
```


### 실행 에러
```
root@Good:/home/jhyunlee/go/src/eBPF/learning-ebpf/chapter5# ./hello-buffer-config 
libbpf: failed to find valid kernel BTF
libbpf: Error loading vmlinux BTF: -3
libbpf: failed to load object 'hello_buffer_config_bpf'
libbpf: failed to load BPF skeleton 'hello_buffer_config_bpf': -3
Failed to open BPF object
root@Good:/home/jhyunlee/go/src/eBPF/learning-ebpf/chapter5# ./hello-buffer-config 
libbpf: failed to find valid kernel BTF
libbpf: Error loading vmlinux BTF: -3
libbpf: failed to load object 'hello_buffer_config_bpf'
libbpf: failed to load BPF skeleton 'hello_buffer_config_bpf': -3
Failed to open BPF object
```
* 원인 : lunux에서 기본으로 제공하는 bcc 패키지를 설치해서 발생한 현상 
* bcc 패키지는 제거한다. 
```
jhyunlee@Good:~/code/libbpf$ apt list | grep bcc

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

bcc/jammy,now 0.16.17-3.3 amd64 [설치됨]

```

* 그러면 다음과 같은 오류가 발생한다.  /usr/include/bpf/bpf_helper.h 파일이 없다는 오류가 나온다. 


```

root@Good:/home/jhyunlee/go/src/eBPF/learning-ebpf/chapter5# make
clang \
    -target bpf \
        -D __TARGET_ARCH_x86 \
    -Wall \
    -O2 -g -o hello-buffer-config.bpf.o -c hello-buffer-config.bpf.c
hello-buffer-config.bpf.c:2:10: fatal error: 'bpf/bpf_helpers.h' file not found
#include <bpf/bpf_helpers.h>
         ^~~~~~~~~~~~~~~~~~~
1 error generated.
make: *** [Makefile:15: hello-buffer-config.bpf.o] 오
```
* 그러면 git를 통해서 다시 clone 받아서 컴파일 한 다음 설치한다. 
* 그러면 실행 파일과 짝이 맞은 helper 파일이 생성되면서 정상 동작한다.  

```
cd ..
git clone --recurse-submodules https://github.com/libbpf/bpftool.git
cd bpftool/src 
make install 


jhyunlee@Good:~/code/libbpf$ git remote -v
origin	https://github.com/libbpf/libbpf.git (fetch)
origin	https://github.com/libbpf/libbpf.git (push)
```