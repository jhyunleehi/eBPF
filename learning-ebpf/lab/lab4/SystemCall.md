# systrem call

사용자 공간 애플리케이션이 커널에게 어떤 작업을 대신 수행하도록 요청할 때 시스템 콜 API를 사용합니다. 따라서 사용자 공간 애플리케이션이 커널에 eBPF 프로그램을 로드하려면 어떤 시스템 콜이 관련되어야 합니다. 사실, bpf()라는 시스템 콜이 있으며, 이 장에서는 이를 사용하여 eBPF 프로그램 및 맵을 로드하고 상호 작용하는 방법을 보여 드리겠습니다.

커널에서 실행되는 eBPF 코드는 맵에 액세스하기 위해 시스템 콜을 사용하지 않습니다. 시스템 콜 인터페이스는 사용자 공간 애플리케이션에 의해서만 사용됩니다. 대신, eBPF 프로그램은 맵에 읽고 쓰기 위해 헬퍼 함수를 사용합니다. 이미 이전 두 장에서 이에 대한 예제를 보았습니다.

만약 여러분이 직접 eBPF 프로그램을 작성하게 된다면, 직접적으로 이 bpf() 시스템 콜을 호출하는 경우는 드뭅니다. 나중에 책에서 논의할 라이브러리들이 있어서 더 높은 수준의 추상화를 제공하여 작업을 쉽게 할 수 있습니다. 그렇다고 해서 이러한 추상화가 일반적으로 이 장에서 볼 수 있는 기본 시스템 콜 명령들과 거의 일대일로 매핑되는 것은 아닙니다. 어떤 라이브러리를 사용하더라도, 여러분은 이 장에서 볼 수 있는 프로그램 로드, 맵 생성 및 액세스 등과 같은 기본 작업에 대한 이해가 필요할 것입니다.
bpf() 시스템 콜의 예를 보여주기 전에, bpf() 맨 페이지에서 무엇을 말하는지 살펴보겠습니다. bpf()를 사용하여 "확장된 BPF 맵 또는 프로그램에 명령을 수행"한다고 합니다. 또한 bpf()의 서명은 다음과 같습니다:

```
int bpf(int cmd, union bpf_attr *attr, unsigned int size);
```
bpf()의 첫 번째 인수인 cmd는 수행할 명령을 지정합니다. bpf() 시스템 콜은 단순히 한 가지 일을 수행하는 것이 아닙니다. eBPF 프로그램 및 맵을 조작하는 데 사용할 수 있는 많은 다른 명령이 있습니다. 아래는 일부 명령어의 개요를 보여주는 Figure 4-1 입니다.

bpf() 시스템 콜의 attr 인수는 명령에 필요한 매개변수를 지정하는 데 필요한 데이터를 보유하고, size는 attr에 포함된 데이터의 바이트 수를 나타냅니다.
이미 1장에서 사용자 공간 코드가 시스템 콜 API를 통해 많은 요청을 만드는 방법을 보여주기 위해 strace를 사용한 적이 있습니다. 이 장에서는 bpf() 시스템 콜이 어떻게 사용되는지를 보여주기 위해 strace를 사용할 것입니다. strace의 출력에는 각 시스템 콜에 대한 인수가 포함되어 있지만, 이 장에서의 예제 출력이 너무 복잡해지지 않도록 하기 위해 특히 흥미로운 경우를 제외하고는 attr 인수의 많은 세부 정보를 생략할 것입니다.


이 예제에서는 2장에서 보았던 예제를 기반으로 하는 hello-buffer-config.py라는 BCC 프로그램을 사용할 것입니다. hello-buffer.py 예제와 마찬가지로, 이 프로그램은 실행될 때마다 perf 버퍼에 메시지를 보내어 execve() 시스템 콜 이벤트에 관한 정보를 커널에서 사용자 공간으로 전달합니다. 이 버전에서 새로운 점은 각 사용자 ID에 대해 다른 메시지를 구성할 수 있도록 하는 것입니다.

```py
#!/usr/bin/python3  
# -*- coding: utf-8 -*-
from bcc import BPF
import ctypes as ct

program = r"""
struct user_msg_t {
   char message[12];
};

BPF_HASH(config, u32, struct user_msg_t);

BPF_PERF_OUTPUT(output); 

struct data_t {     
   int pid;
   int uid;
   char command[16];
   char message[12];
};

int hello(void *ctx) {
   struct data_t data = {}; 
   struct user_msg_t *p;
   char message[12] = "Hello World";

   data.pid = bpf_get_current_pid_tgid() >> 32;
   data.uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;

   bpf_get_current_comm(&data.command, sizeof(data.command));

   p = config.lookup(&data.uid);
   if (p != 0) {
      bpf_probe_read_kernel(&data.message, sizeof(data.message), p->message);       
   } else {
      bpf_probe_read_kernel(&data.message, sizeof(data.message), message); 
   }

   output.perf_submit(ctx, &data, sizeof(data)); 
 
   return 0;
}
"""

b = BPF(text=program) 
syscall = b.get_syscall_fnname("execve")
b.attach_kprobe(event=syscall, fn_name="hello")
b["config"][ct.c_int(0)] = ct.create_string_buffer(b"Hey root!")
b["config"][ct.c_int(501)] = ct.create_string_buffer(b"Hi user 501!")
 
def print_event(cpu, data, size):  
   data = b["output"].event(data)
   print(f"{data.pid} {data.uid} {data.command.decode()} {data.message.decode()}")
 
b["output"].open_perf_buffer(print_event) 
while True:   
   b.perf_buffer_poll()
```

1. 이 줄은 12글자의 메시지를 저장하기 위한 user_msg_t라는 구조체 정의가 있음을 나타냅니다.
2. BCC 매크로인 BPF_HASH는 config라는 해시 테이블 맵을 정의하는 데 사용됩니다. 이 맵은 user_msg_t 유형의 값들을 u32 유형의 키로 색인화하여 보유할 것입니다. (키와 값의 유형을 지정하지 않으면, BCC는 기본적으로 키와 값 모두 u64로 설정됩니다.)
3. perf 버퍼 출력은 2장과 완전히 동일한 방식으로 정의됩니다. 버퍼에 임의의 데이터를 제출할 수 있으므로 여기서는 데이터 유형을 지정할 필요가 없습니다...

4. ...하지만 실제로, 이 예제에서 프로그램은 항상 data_t 구조체를 제출합니다. 이것은 2장의 예제와 마찬가지로 변경되지 않았습니다.
5. 이 eBPF 프로그램의 나머지 부분은 앞서 본 hello() 버전과 변경되지 않았습니다.
6. 유저 ID를 얻기 위해 헬퍼 함수를 사용한 유일한 차이점은 코드가 해당 유저 ID를 키로 하는 config 해시 맵에서 항목을 찾습니다. 일치하는 항목이 있는 경우, 해당 값에는 기본 "Hello World" 대신 사용할 메시지가 포함되어 있습니다.
```
b["config"][ct.c_int(0)] = ct.create_string_buffer(b"Hey root!")
b["config"][ct.c_int(501)] = ct.create_string_buffer(b"Hi user 501!")
```







cd /home/jhyunlee/code/eBPF ; 

/usr/bin/env sudo 
-E /bin/python3 /home/jhyunlee/.vscode/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher 48067 
-- /home/jhyunlee/code/eBPF/learning-ebpf/chapter4/hello-buffer-config.py 
-v -s --debuglevel==DEBUG 


