# eBPF

## architecutre 
* eBPF progrma are loaded and executed in Kernel
* eBPF verifier
  1. Ensuer ther BPF programs aree sage and crash-free
  2. Rejects if it is deemed to be unsage
  3. Not allowing looping or backward branches

* JIT compiler 
translates the generic byte-code of the proogram into machine specific instruction set
* eBPF MAPS 
provides ability to share the coolectied information between the kernel and user space

## Dynamic loading of eBPF program
* eBPF programss  can be loaded into and removed froom ther nernel dynamically
* Once they are attached to the event, triggered regardless of the cause of the event 
* pre-defined hooks
  1. System Calls, cuntions@ Entry/Exit
  2. Kernel trace Point
  3. Network event and serveral other places 

* Example 
    1. Attach the BPF program at the entry of open system call it will be triggerd whenerve any process tries to open the fil e
    2. Attach the BPF program at the entry go execv system call it will be triggered whenever a new binary application is executed
* This leads to one of the greates strength of obsservability or security toling that uses 




