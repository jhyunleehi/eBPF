# 어느 것을 사용할 것인가 ?
##  kprobe  and  ftrace (/sys/kernel/debug/tracing) 차이점 

When learning about the Linux kernel, understanding the difference between Kprobes and Ftrace can be crucial, as they are both tools used for kernel debugging and tracing, but they serve different purposes and operate at different levels of the kernel.

Kprobes: Kprobes is a dynamic kernel debugging mechanism that allows developers to insert breakpoints (probes) into running kernel code. These probes can be used to monitor the execution flow of the kernel, gather information about specific events, or debug kernel code without requiring recompilation or rebooting the system. Kprobes allows developers to attach "probe handlers" to specific locations in the kernel code, which are executed when the probe is hit. This mechanism is particularly useful for debugging complex kernel issues or analyzing kernel behavior in real-time.

Ftrace: Ftrace, on the other hand, is a kernel tracing framework that provides a set of tools for tracing various kernel events and functions. It allows developers to dynamically instrument the kernel to collect detailed information about its behavior, such as function call traces, context switches, interrupt activity, and more. Ftrace provides a powerful interface for analyzing kernel performance, identifying bottlenecks, and diagnosing issues. It consists of several components, including function tracer, function graph tracer, event tracer, and tracepoints. Ftrace is typically used for performance analysis, optimization, and understanding kernel internals.

Here's a summary of the key differences between Kprobes and Ftrace:
#### Purpose: 
* kprobe : 커널 코드에 대한 동적 디버깅하기 위해서 handler 커널에 코드를 집어 넣는 것
* ftrace : 커널 활동을 tracing 하고 성능을 분석하기위한 것
* Kprobes is primarily used for dynamic kernel debugging by inserting probes into running kernel code to monitor specific events or gather information
* Ftrace is used for tracing kernel activities and performance analysis.

#### Granularity: 
* kprobe : instruction level에서 커널의 동작을 확인하기 위해서 디거깅용 코그를 넣기 때문에 더 작은 단위
* ftrace : 좀더 high level에서  system  call, event 등을 tracing 하는 것 
* Kprobes operates at the instruction level, allowing developers to insert probes at specific locations within kernel code
* Ftrace operates at a higher level, tracing function calls, events, and system activities.

#### Flexibility: 
* kprobe : 커널 코드에 대한 세밀한 제어를 할 수 있다. 
* ftrace : 추적 기능과 분석 도구가 내장된 framework 
* Kprobes provides fine-grained control over the instrumentation of kernel code and allows developers to specify custom probe handlers
* Ftrace provides a more high-level tracing framework with built-in tracing capabilities and analysis tools.

#### Use Cases: 
* kprobe : 커널의 특정한 이슈에 대한 디버깅, 커널 개발자가 사용하는 도구
* ftrace :  성능 분석 및 최적화 커널의 전반적 동작을 이해하는데 사용 
* Kprobes is typically used for debugging specific kernel issues or analyzing kernel behavior in real-time
* Ftrace is used for performance analysis, optimization, and understanding the overall behavior of the kernel.

In summary, while both Kprobes and Ftrace are powerful tools for kernel debugging and tracing, they serve different purposes and offer different levels of granularity and flexibility. Developers may choose to use one or both of these tools depending on their specific debugging and tracing requirements.


## 결론 
* 커널 수준의 개발자가 이슈 디버깅을 위해서는 kprobe를 사용하는 것이 맞고 
    - BPF: kbpobes
    - BPF: kretprobe
* 성능 분석 및 모니터링 정도를 하려면 ftrace를 이용한 eBPF를 사용하는 것이 맞다.  
    - BPF: tracepoint 

```
TRACEPOINT_PROBE(random, urandom_read) {
    // args is from /sys/kernel/debug/tracing/events/random/urandom_read/format
    bpf_trace_printk("%d\\n", args->got_bits);
    return 0;
}
```