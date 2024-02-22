# Hello World 

```py
#!/usr/bin/python3  
from bcc import BPF

program = r"""
int hello(void *ctx) {
    bpf_trace_printk("Hello World!");
    return 0;
}
"""

b = BPF(text=program)
syscall = b.get_syscall_fnname("execve")
b.attach_kprobe(event=syscall, fn_name="hello")

b.trace_print()
```
* eBPF 프로그램은 bpf_trace_printk()와 같은 helper 함수를 사용하여 메시지를 작성합니다. 헬퍼 함수는 "확장된" BPF를 "클래식" 이전 버전과 구별하는 또 다른 기능입니다. 이러한 함수들은 eBPF 프로그램이 시스템과 상호 작용할 수 있는 함수 집합이다.  
* 전체 eBPF 프로그램은 Python 코드에서 program이라는 문자열로 정의됩니다. 이 C 프로그램은 실행되기 전에 컴파일되어야 하지만, BCC가 그것을 처리합니다. (다음 장에서 eBPF 프로그램을 직접 컴파일하는 방법을 볼 것입니다.) BPF 객체를 생성할 때 이 문자열을 매개변수로 전달하면 됩니다. 


```py 
    # Given a syscall's name, return the full Kernel function name with current
    # system's syscall prefix. For example, given "clone" the helper would
    # return "sys_clone" or "__x64_sys_clone".
    def get_syscall_fnname(self, name):
        name = _assert_is_bytes(name)
        return self.get_syscall_prefix() + name

    # Find current system's syscall prefix by testing on the BPF syscall.
    # If no valid value found, will return the first possible value which
    # would probably lead to error in later API calls.
    def get_syscall_prefix(self):
        for prefix in self._syscall_prefixes:
            if self.ksymname(b"%sbpf" % prefix) != -1:
                return prefix
        return self._syscall_prefixes[0]        

    def ksymname(name):
        """ksymname(name)

        Translate a kernel name into an address. This is the reverse of
        ksym. Returns -1 when the function name is unknown."""
        return BPF._sym_cache(-1).resolve_name(None, name)

    def _sym_cache(pid): 
        """_sym_cache(pid)
        Returns a symbol cache for the specified PID.
        The kernel symbol cache is accessed by providing any PID less than zero.
        """
        if pid < 0 and pid != -1:
            pid = -1
        if not pid in BPF._sym_caches:
            BPF._sym_caches[pid] = SymbolCache(pid)
        return BPF._sym_caches[pid]

    _syscall_prefixes = [
        b"sys_",
        b"__x64_sys_",
        b"__x32_compat_sys_",
        b"__ia32_compat_sys_",
        b"__arm64_sys_",
        b"__s390x_sys_",
        b"__s390_sys_",
    ]        
```        
* 이제 syscall은 kprobe를 사용하여 연결할 커널 함수의 이름

## map
* 제일 궁금한 것은 BPF_HASH(counter_table) 이것이 어디에 정의 되어 있는가?
* BPF_HASH() is a BCC macro that defines a hash table map. 라고 하는데 어디에 정의되어 있는지를 모르겠네..
* 무슨 소스 코드가 이렇게 되어 있냐?
  - You can navigate to the src/cc directory and find the bpf_helpers.h file where the BPF_HASH() macro is defined
  - The source code for the BPF_HASH() macro in BCC (BPF Compiler Collection) can be found in the BCC GitHub repository. 
  - BCC is an open-source project, and its source code is hosted on GitHub. 
  - You can find the definition of the BPF_HASH() macro in the bpf_helpers.h header file within the BCC repository.
  - 이것이 macro 인데 실제 파일에 가서 보면  
* bcc repository에서  소스 코드가 이렇게 되어 있는 것은 무엇을 의미하냐 ?  R"********(  
이런 사연이 있었구만 ...

소스 코드가 R"********(와 같은 형태로 시작되는 것은 C++11부터 도입된 Raw String Literal 문법을 나타냅니다. 이 문법을 사용하면 문자열을 이스케이프 문자 없이 그대로 표현할 수 있습니다. "********"는 임의의 종료 문자열로, 소스 코드 내에서 나오는 문자열이 이 문자열로 끝나는 것을 나타냅니다.


```
#define BPF_HASH(...) \
  BPF_HASHX(__VA_ARGS__, BPF_HASH4, BPF_HASH3, BPF_HASH2, BPF_HASH1)(__VA_ARGS__)
```


```
#!/usr/bin/python3  
from bcc import BPF
from time import sleep

program = r"""
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
"""

b = BPF(text=program)
syscall = b.get_syscall_fnname("execve")
b.attach_kprobe(event=syscall, fn_name="hello")

# Attach to a tracepoint that gets hit for all syscalls 
# b.attach_raw_tracepoint(tp="sys_enter", fn_name="hello")

while True:
    sleep(2)
    s = ""
    for k,v in b["counter_table"].items():
        s += f"ID {k.value}: {v.value}\t"
    print(s)

```


* BPF_HASH() is a BCC macro that defines a hash table map.


