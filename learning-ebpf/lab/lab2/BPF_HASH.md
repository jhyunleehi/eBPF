## BPF_HASH macro 

BPF_HASH 매크로는 리눅스의 eBPF (extended Berkeley Packet Filter) 시스템에서 사용되는 매크로 중 하나입니다. 이것은 BPF (Berkeley Packet Filter)의 확장된 버전으로, 커널 내에서 실행되는 프로그램을 통해 네트워크 트래픽을 필터링하고 조작하는 데 사용됩니다. BPF 프로그램은 커널 공간에서 안전하게 실행되며, 이를 통해 성능 향상과 보안을 달성할 수 있습니다.

BPF_HASH 매크로는 해시 맵을 만들기 위해 사용됩니다. 해시 맵은 키-값 쌍을 저장하는 데이터 구조로, 빠른 검색과 삽입이 가능합니다. BPF 프로그램 내에서 상태를 유지하거나 데이터를 저장하기 위해 BPF_HASH를 사용할 수 있습니다.

예를 들어, BPF_HASH를 사용하여 특정 IP 주소에 대한 패킷 수를 추적할 수 있습니다. 이는 패킷이 특정 IP 주소로 전송되었을 때 BPF 프로그램에서 해당 IP 주소에 대한 카운터를 증가시키는 방식으로 동작합니다.

다음은 간단한 BPF_HASH 예제입니다:


```c
#include <linux/bpf.h>

// BPF_HASH 정의
BPF_HASH(ip_pkt_count, u32, u64);

int packet_handler(struct __sk_buff *skb) {
    u32 key = skb->remote_ip4;
    u64 *count = ip_pkt_count.lookup(&key);

    if (count) {
        (*count)++;
    } else {
        u64 new_count = 1;
        ip_pkt_count.update(&key, &new_count);
    }

    return 0;
}
```
이 예제에서는 "ip_pkt_count"라는 이름의 해시 맵을 정의하고, u32 형식의 키(여기서는 IP 주소)와 u64 형식의 값(패킷 수)을 가집니다. "packet_handler" 함수에서는 각 패킷이 도착할 때마다 해당 IP 주소에 대한 카운터를 증가시킵니다. 만약 해당 IP 주소에 대한 카운터가 아직 없다면 새로운 항목을 추가합니다.

이것은 매우 간단한 예제이며, 실제로는 더 복잡한 로직이 필요할 수 있습니다. 하지만 이것은 BPF_HASH를 사용하여 상태를 유지하고 데이터를 추적하는 방법을 보여줍니다.


```c
BPF_HASH(counter_table);

int hello(void *ctx) {
   u64 uid;
   u64 counter = 0;
   u64 *p;

   uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
   p = counter_table.lookup(&uid);
   if (p != 0) {
      counter = *p;
   }
   counter++;
   counter_table.update(&uid, &counter);
   return 0;
}
```

### BPF_HASH() macro is  /uapi/linu
The BPF_HASH() macro is defined in the bpf_common.h header file within the Linux kernel source code. 

This file contains common definitions and macros used by various parts of the BPF subsystem. 
You can find this header file typically located in the include/uapi/linux/ directory of the kernel source tree.

Here's a simplified version of how BPF_HASH() might be defined:

```c
#define BPF_HASH(name, key_type, value_type) \
    struct bpf_map_def SEC("maps") name = {  \
        .type = BPF_MAP_TYPE_HASH,           \
        .key_size = sizeof(key_type),        \
        .value_size = sizeof(value_type),    \
        .max_entries = 10240,                \
    }
```
* This macro defines a BPF hash map named name with a given key_type and value_type. 
* The max_entries field specifies the maximum number of entries the hash map can hold. 
* The SEC("maps") section specifier is used to place the map definition in a specific section, which is necessary for BPF maps to be loaded into the kernel properly.

* Keep in mind that the actual definition might be more complex in the kernel source code, but this simplified version gives you an idea of how it works.


