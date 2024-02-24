# Tracing and Visualizing File System Internals with eBPF
## hello world
```c
#include <stdio.h>
char filename[] = "output.txt";
char message[] = "hello, world!\n";
FILE * file;
void rcall(int n){
    if (n<0) return;
    fputs( message, file);    
    fprintf(file,"[%d]:%s", n, message);
    rcall(n-1);
}
int main()
{
    file = fopen(filename, "w");
    if (file == NULL) return -1;    
    rcall(10);
    fclose(file);
    return 0;
}
```
```sh
$ gcc -g -pg -o hello hello.c
```
## Filesystem Internal
* sys_open
* vfs_open
* ext_file_open
* block devices
* HDD driver
* disk
[linux Kernel Map](https://makelinux.github.io/kernel/map)
[Storage function](https://en.wikibooks.org/wiki/The_Linux_Kernel/Storage)
## tracing with ftrace
ftrace 란
 
ftrace 리눅스 커널에서 제공하는 가장 강력한 트레이서입니다.
1. 인터럽트, 스케줄링, 커널 타이머 커널 동작을 상세히 추적해줍니다.
2. 함수 필터를 지정하면 자신을 호출한 함수와 전체 콜스택까지 출력합니다. 물론 코드를 수정할 필요가 습니다.
3. 함수를 어느 프로세스가 실행하는지 알 수 있습니다.
4. 함수 실행 시각을 알 수 있습니다.
5. ftrace 로그를 키면 시스템 동작에 부하를 주지 않습니다.
### 이벤트 (event)
* available_event
* `ls /sys/kernel/debug/tracing/available_events`
```
pi@raspberrypi:~$ sudo su -
root@raspberrypi:~# cd /sys/kernel/debug/tracing
root@raspberrypi:/sys/kernel/debug/tracing# ls -l available_*
-r--r--r-- 1 root root 0 Jan  1  1970 available_events
-r--r--r-- 1 root root 0 Jan  1  1970 available_filter_functions
-r--r--r-- 1 root root 0 Jan  1  1970 available_tracer
```
#### setf.sh
```
root@gpu-1:/sys/kernel/debug/tracing
# chmod 755 ~/setf.sh
root@gpu-1:/sys/kernel/debug/tracing# vi ~/setf.sh
```
```sh
#!/bin/bash
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 0 > /sys/kernel/debug/tracing/events/enable
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/events/sched/sched_wakeup/enable
echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable
echo 1 > /sys/kernel/debug/tracing/events/irq/irq_handler_entry/enable
echo 1 > /sys/kernel/debug/tracing/events/irq/irq_handler_exit/enable
echo 1 > /sys/kernel/debug/tracing/events/raw_syscalls/enable
echo 1 > /sys/kernel/debug/tracing/options/func_stack_trace
echo 1 > /sys/kernel/debug/tracing/options/sym-offset
echo 1 > /sys/kernel/debug/tracing/tracing_on
```
### tracer 설정
ftrace는 nop, function, graph_function 트레이서를 제공합니다.
* nop: 기본 트레이서입니다. ftrace 이벤트만 출력합니다.**
* function: 함수 트레이서입니다. set_ftrace_filter로 지정한 함수를 누가 호출하는지 출력합니다.**
* graph_function: 함수 실행 시간과 세부 호출 정보를 그래프 포맷으로 출력합니다.**
```
root@raspberrypi:/sys/kernel/debug/tracing# cat current_tracer
nop
```
## tracing with uftrace
```sh
$ gdb  ./hello
(gdb) list
(gdb) break 5
(gdb) run
(gdb) info frame
(gdb) info files
(gdb) info local
(gdb) info proc
(gdb) info break
(gdb) print VAL
(gdb) display i
(gdb) disas main
$ stat ./hello
$ perf record -a -g  ./hello
$ perf report --header  -F overhead,comm,parent
$ perf stat ./hello
$ strace ./hello
$ stat  ./hello
$ sudo uftrace -K 5 ./hello
$ sudo uftrace record -K 5 ./hello
$ sudo uftrace tui
```
##  uftrace
```log
root@gpu-1:~# uftrace repla
uftrace: ./cmds/record.c:1542:find_in_path
 ERROR: Cannot trace 'repla': No such executable file.
root@gpu-1:~# uftrace record  -a  hello
root@gpu-1:~# uftrace replay
# DURATION     TID     FUNCTION
   0.552 us [171032] | __monstartup();
   0.121 us [171032] | __cxa_atexit();
            [171032] | main() {
 248.661 us [171032] |   fopen("output.txt", "w") = 0x5624e930c960;
            [171032] |   rcall(10) {
   3.810 us [171032] |     fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.724 us [171032] |     fprintf(0x5624e930c960, "[%d]:%s") = 19;
            [171032] |     rcall(9) {
   0.164 us [171032] |       fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.203 us [171032] |       fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |       rcall(8) {
   1.403 us [171032] |         fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.152 us [171032] |         fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |         rcall(7) {
   0.095 us [171032] |           fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.148 us [171032] |           fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |           rcall(6) {
   0.094 us [171032] |             fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.142 us [171032] |             fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |             rcall(5) {
   0.092 us [171032] |               fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.149 us [171032] |               fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |               rcall(4) {
   1.297 us [171032] |                 fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.151 us [171032] |                 fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |                 rcall(3) {
   0.092 us [171032] |                   fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.141 us [171032] |                   fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |                   rcall(2) {
   0.089 us [171032] |                     fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.146 us [171032] |                     fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |                     rcall(1) {
   0.089 us [171032] |                       fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.146 us [171032] |                       fprintf(0x5624e930c960, "[%d]:%s") = 18;
            [171032] |                       rcall(0) {
   1.294 us [171032] |                         fputs("hello, world!\n", 0x5624e930c960) = 1;
   0.206 us [171032] |                         fprintf(0x5624e930c960, "[%d]:%s") = 18;
   0.073 us [171032] |                         rcall(-1);
   2.031 us [171032] |                       } /* rcall */
   2.643 us [171032] |                     } /* rcall */
   3.217 us [171032] |                   } /* rcall */
   3.791 us [171032] |                 } /* rcall */
   5.591 us [171032] |               } /* rcall */
   6.173 us [171032] |             } /* rcall */
   6.735 us [171032] |           } /* rcall */
   7.308 us [171032] |         } /* rcall */
   9.224 us [171032] |       } /* rcall */
   9.979 us [171032] |     } /* rcall */
  15.392 us [171032] |   } /* rcall */
  37.456 us [171032] |   fclose(0x5624e930c960) = 0;
 302.814 us [171032] | } = 0; /* main */
```
### uftrace -K 5  -a  ./hello
#### file open, read, write, close
```log
# DURATION     TID     FUNCTION
   0.635 us [171545] | __monstartup();
   0.114 us [171545] | __cxa_atexit();
            [171545] | main() {
            [171545] |   fopen("output.txt", "w") {
# sys_open                
            [171545] |     __x64_sys_openat() {
            [171545] |       do_sys_openat2() {
            [171545] |         getname() {
            [171545] |           getname_flags.part.0() {
   0.502 us [171545] |             kmem_cache_alloc();
   0.691 us [171545] |             __check_object_size();
   1.755 us [171545] |           } /* getname_flags.part.0 */
   2.094 us [171545] |         } /* getname */
            [171545] |         get_unused_fd_flags() {
            [171545] |           alloc_fd() {
   0.149 us [171545] |             _raw_spin_lock();
   0.172 us [171545] |             expand_files();
   0.147 us [171545] |             _raw_spin_unlock();
   1.202 us [171545] |           } /* alloc_fd */
   1.533 us [171545] |         } /* get_unused_fd_flags */
            [171545] |         do_filp_open() {
            [171545] |           path_openat() {
   2.522 us [171545] |             alloc_empty_file();
   0.454 us [171545] |             path_init();
   6.524 us [171545] |             link_path_walk.part.0.constprop.0();
   1.415 us [171545] |             open_last_lookups();
   9.924 us [171545] |             do_open();
   0.910 us [171545] |             terminate_walk();
  23.088 us [171545] |           } /* path_openat */
  23.451 us [171545] |         } /* do_filp_open */
   0.154 us [171545] |         fd_install();
            [171545] |         putname() {
   0.186 us [171545] |           kmem_cache_free();
   0.516 us [171545] |         } /* putname */
  28.879 us [171545] |       } /* do_sys_openat2 */
  29.232 us [171545] |     } /* __x64_sys_openat */
...
# sys_read
            [171545] |     __x64_sys_read() {
            [171545] |       ksys_read() {
            [171545] |         __fdget_pos() {
   0.155 us [171545] |           __fget_light();
   0.503 us [171545] |         } /* __fdget_pos */
            [171545] |         vfs_read() {
            [171545] |           rw_verify_area() {
   0.565 us [171545] |             security_file_permission();
   0.900 us [171545] |           } /* rw_verify_area */
            [171545] |           seq_read() {
   0.158 us [171545] |             __get_task_ioprio();
  51.269 us [171545] |             seq_read_iter();
  51.974 us [171545] |           } /* seq_read */
  53.483 us [171545] |         } /* vfs_read */
  54.521 us [171545] |       } /* ksys_read */
  54.935 us [171545] |     } /* __x64_sys_read */
...
# sys_write
            [171545] |     __x64_sys_write() {
            [171545] |       ksys_write() {
            [171545] |         __fdget_pos() {
   0.164 us [171545] |           __fget_light();
   0.506 us [171545] |         } /* __fdget_pos */
            [171545] |         vfs_write() {
            [171545] |           rw_verify_area() {
   0.564 us [171545] |             security_file_permission();
   0.904 us [171545] |           } /* rw_verify_area */
   0.147 us [171545] |           __cond_resched();
   0.151 us [171545] |           __get_task_ioprio();
            [171545] |           ext4_file_write_iter() {
  25.975 us [171545] |             ext4_buffered_write_iter();
  26.336 us [171545] |           } /* ext4_file_write_iter */
   0.254 us [171545] |           __fsnotify_parent();
   0.153 us [171545] |           irq_enter_rcu();
            [171545] |           __sysvec_irq_work() {
   0.506 us [171545] |             __wake_up();
   0.500 us [171545] |             __wake_up();
   1.596 us [171545] |           } /* __sysvec_irq_work */
            [171545] |           irq_exit_rcu() {
   0.192 us [171545] |             idle_cpu();
   0.540 us [171545] |           } /* irq_exit_rcu */
  32.355 us [171545] |         } /* vfs_write */
  33.392 us [171545] |       } /* ksys_write */
  33.743 us [171545] |     } /* __x64_sys_write */
...
# sys_close
            [171545] |     __x64_sys_close() {
            [171545] |       close_fd() {
   0.154 us [171545] |         _raw_spin_lock();
   0.155 us [171545] |         pick_file();
   0.151 us [171545] |         _raw_spin_unlock();
            [171545] |         filp_close() {
   0.161 us [171545] |           dnotify_flush();
   0.162 us [171545] |           locks_remove_posix();
            [171545] |           fput() {
   0.260 us [171545] |             task_work_add();
   0.617 us [171545] |           } /* fput */
   1.703 us [171545] |         } /* filp_close */
   3.108 us [171545] |       } /* close_fd */
   3.458 us [171545] |     } /* __x64_sys_close */
```
### availabel filter_function
 * find supported kernel funtion  
```
root@gpu-2:/sys/kernel/debug/tracing# egrep  "ksys_read|ksys_write|close_fd|do_sys_openat2" avail*
available_filter_functions:do_sys_openat2
available_filter_functions:ksys_read
available_filter_functions:ksys_write
available_filter_functions:close_fd
available_filter_functions:ksys_readahead
```
* not support __x86_sys_open, __x86_sys_read, __x86_sys_read, __x86_sysclose
```
./setf1.sh: line 6: echo: write error: Invalid argument
./setf1.sh: line 7: echo: write error: Invalid argument
```
## ftrace set :  file open,read,write,close
```sh
#!/bin/bash
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 0 > /sys/kernel/debug/tracing/events/enable
echo function > /sys/kernel/debug/tracing/current_tracer
echo do_sys_openat2  > /sys/kernel/debug/tracing/set_ftrace_filter
echo ksys_read   >> /sys/kernel/debug/tracing/set_ftrace_filter
echo ksys_write  >> /sys/kernel/debug/tracing/set_ftrace_filter
echo close_fd  >> /sys/kernel/debug/tracing/set_ftrace_filter
echo 1 > /sys/kernel/debug/tracing/options/func_stack_trace
echo 1 > /sys/kernel/debug/tracing/options/sym-offset
echo 1 > /sys/kernel/debug/tracing/tracing_on
```
```sh
#!/bin/bash
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 0 > /sys/kernel/debug/tracing/events/enable
echo 0 > /sys/kernel/debug/tracing/options/stacktrace
cp  /sys/kernel/debug/tracing/trace ftrace.log
```
#### ftrace log
```
           hello-35266   [003] ..... 253247.232634: do_sys_openat2+0x0/0xe0 <-__x64_sys_openat+0x6c/xa0
           hello-35266   [003] ..... 253247.232635: <stack trace>
 => do_sys_openat2+0x5/0xe0
 => __x64_sys_openat+0x6c/0xa0
 => do_syscall_64+0x58/0x90
 => entry_SYSCALL_64_after_hwframe+0x6e/0xd8
           hello-35266   [003] ..... 253247.232454: ksys_read+0x0/0x100 <-__x64_sys_read+0x19/0x30
           hello-35266   [003] ..... 253247.232454: <stack trace>
 => ksys_read+0x5/0x100
 => __x64_sys_read+0x19/0x30
 => do_syscall_64+0x58/0x90
 => entry_SYSCALL_64_after_hwframe+0x6e/0xd8
            hello-35266   [003] ..... 253247.232728: ksys_write+0x0/0x100 <-__x64_sys_write+0x19/0x30
           hello-35266   [003] ..... 253247.232729: <stack trace>
 => ksys_write+0x5/0x100
 => __x64_sys_write+0x19/0x30
 => do_syscall_64+0x58/0x90
 => entry_SYSCALL_64_after_hwframe+0x6e/0xd8
            hello-35266   [003] ..... 253247.232684: close_fd+0x0/0x70 <-__x64_sys_close+0x11/0x50
           hello-35266   [003] ..... 253247.232685: <stack trace>
 => close_fd+0x5/0x70
 => __x64_sys_close+0x11/0x50
 => do_syscall_64+0x58/0x90
 => entry_SYSCALL_64_after_hwframe+0x6e/0xd8
 ```
####  set_ftrace_filter 설정
* set_ftrace_filter 파일에 트레이싱하고 싶은 함수를 지정하면 된다.
* 위의 tracer 설정의 function 혹은 function_graph으로 설정한 경우 작동하는 파일이다.
* 리눅스 커널에 존재하는 모든 함수를 필터로 지정할 수는 없다. /sys/kernel/debug/tracing/available_filter_functions 파일에 포함된 함수만 지정할 수 있다.
* 함수를 지정하지 않은 경우 모든 함수를 트레이싱하게 되어 락업이 상태에 빠지게 된다.
* available_filter_functions 파일에 없는 함수를 지정하려도 락업 상태가 될 수 있으니 주의하자.
* set_ftrace_filter에 아무것도 설정하지 않고 ftrace를 키면, ftrace는 모든 커널 함수에 대하여 트레이싱을 한다.
* 모든 커널 함수에 의해 트레이스가 발생되면, 그 오버헤드가 엄청나 시스템은 락업 상태에 빠진다.
* 그러므로 부팅 이후 절대 불리지 않을 함수secondary_start_kernel2를 트레이스 포인트로 찍어준다.
### check FONFIG_FUNCTION_TRACER
```
root@gpu-1:~# grep  CONFIG_FUNCTION  /boot/config-6.5.0-17-generic
CONFIG_FUNCTION_TRACER=y
```
# trace-cmd
* interacts with ftrace linuc kernel internal tracer
* ftrace front utility

```c
# apt  install trace-cmd
# trace-cmd  record -p function ./hello
# trace-cmd  record -p function ./hello  
# trace-cmd  record -p function-graph ./hello  
# trace-cmd  record -p function ./hello  
# trace-cmd  repoort >t.log  
```
#### trace-cmd report
* too big and larg log
```go
root@gpu-2:~# ls -lh trace.dat
-rw-r--r-- 1 root root 14M  2월 18 16:29 trace.dat
root@gpu-2:~# ls -lh t.log
-rw-r--r-- 1 root root 3.6M  2월 18 16:28 t.log
root@gpu-2:~# wc -l t.log
37691 t.log
CPU 3 is empty
CPU 4 is empty
CPU 7 is empty
CPU 11 is empty
cpus=12
           hello-36916 [010] 254630.435515: function:             mutex_unlock
           hello-36916 [010] 254630.435516: function:             __f_unlock_pos
           hello-36916 [010] 254630.435516: function:                mutex_unlock
           hello-36916 [010] 254630.435517: function:             exit_to_user_mode_prepare
           hello-36916 [010] 254630.435517: function:                exit_to_user_mode_loop
           hello-36916 [010] 254630.435517: function:                   mem_cgroup_handle_over_high
           hello-36916 [010] 254630.435517: function:                   blkcg_maybe_throttle_current
           hello-36916 [010] 254630.435517: function:                   __rseq_handle_notify_resume
           hello-36916 [010] 254630.435518: function:                      rseq_ip_fixup
           hello-36916 [010] 254630.435518: function:                         rseq_get_rseq_cs
           hello-36916 [010] 254630.435518: function:                      rseq_update_cpu_node_id
           hello-36916 [010] 254630.435518: function:                fpregs_assert_state_consistent
           hello-36916 [010] 254630.435519: function:                switch_fpu_return
           hello-36916 [010] 254630.435522: function:             __x64_sys_execve
           hello-36916 [010] 254630.435522: function:                getname
           hello-36916 [010] 254630.435523: function:                   getname_flags.part.0
           hello-36916 [010] 254630.435523: function:                      kmem_cache_alloc
           hello-36916 [010] 254630.435523: function:                         __cond_resched
           hello-36916 [010] 254630.435523: function:                         should_failslab
           hello-36916 [010] 254630.435524: function:             __check_object_size
           hello-36916 [010] 254630.435524: function:                __check_object_size.part.0
           hello-36916 [010] 254630.435524: function:                   check_stack_object
           hello-36916 [010] 254630.435525: function:             is_vmalloc_addr
           hello-36916 [010] 254630.435525: function:             __virt_addr_valid
           hello-36916 [010] 254630.435526: function:             __check_heap_object        
```
#### ksys_read trace
```log
           hello-36916 [010] 254630.440930: function:             __x64_sys_read
           hello-36916 [010] 254630.440930: function:                ksys_read
           hello-36916 [010] 254630.440930: function:                   __fdget_pos
           hello-36916 [010] 254630.440930: function:                      __fget_light
           hello-36916 [010] 254630.440931: function:                   vfs_read
           hello-36916 [010] 254630.440931: function:                      rw_verify_area
           hello-36916 [010] 254630.440931: function:                         security_file_permission
           hello-36916 [010] 254630.440931: function:                            apparmor_file_permission
           hello-36916 [010] 254630.440931: function:                               aa_file_perm
           hello-36916 [010] 254630.440931: function:                                  __rcu_read_lock
           hello-36916 [010] 254630.440931: function:                                  __rcu_read_unlock
           hello-36916 [010] 254630.440931: function:             __fsnotify_parent
           hello-36916 [010] 254630.440932: function:                      __get_task_ioprio
           hello-36916 [010] 254630.440932: function:                      ext4_file_read_iter
           hello-36916 [010] 254630.440932: function:                         generic_file_read_iter
           hello-36916 [010] 254630.440932: function:                            filemap_read
           hello-36916 [010] 254630.440932: function:                               __cond_resched
           hello-36916 [010] 254630.440932: function:                               filemap_get_pages
           hello-36916 [010] 254630.440932: function:                                  filemap_get_read_batch
           hello-36916 [010] 254630.440932: function:                                     __rcu_read_lock
           hello-36916 [010] 254630.440933: function:                                     __rcu_read_unlock
           hello-36916 [010] 254630.440933: function:                               folio_mark_accessed
           hello-36916 [010] 254630.440933: function:                               touch_atime
           hello-36916 [010] 254630.440933: function:                                  atime_needs_update
           hello-36916 [010] 254630.440933: function:                                     make_vfsuid
           hello-36916 [010] 254630.440934: function:                                     make_vfsgid
           hello-36916 [010] 254630.440934: function:                                     current_time
           hello-36916 [010] 254630.440934: function:                                        ktime_get_coarse_real_ts64
           hello-36916 [010] 254630.440934: function:                      __fsnotify_parent
```
## perf : Performan analysis tools for linus
### perf stat
```log
root@gpu-1:~# perf stat ./hello
 Performance counter stats for './hello':
              0.49 msec task-clock                       #    0.541 CPUs utilized            
                 0      context-switches                 #    0.000 /sec                      
                 0      cpu-migrations                   #    0.000 /sec                      
                63      page-faults                      #  127.476 K/sec                    
         2,048,928      cycles                           #    4.146 GHz                      
         1,376,140      instructions                     #    0.67  insn per cycle            
           245,301      branches                         #  496.350 M/sec                    
             8,908      branch-misses                    #    3.63% of all branches          
       0.000914125 seconds time elapsed
       0.000985000 seconds user
       0.000000000 seconds sys
```

## bcc
#### install ubunut package 
* 이렇게 설치하면 라이브러리가 잘 안맞아서 오류 발생
* 괜히 python3 설치 다시 했다가 ubuntu-desktop 망가진다. 



```bash
sudo apt install calng
sudo apt-get install bpfcc-tools linux-headers-$(uname -r)
```
The tools are installed in `/sbin` (`/usr/sbin` in Ubuntu 18.04) with a `-bpfcc` extension. Try running `sudo opensnoop-bpfcc`.
```
root@gpu-2:/usr/sbin# ./opensnoop.bt
Attaching 6 probes...
ERROR: Could not resolve symbol: /proc/self/exe:BEGIN_trigger
```
#### error
```python
root@gpu-2:/usr/sbin# ./biotop-bpfcc
In file included from <built-in>:2:
In file included from /virtual/include/bcc/bpf.h:12:
In file included from include/linux/types.h:6:
In file included from include/uapi/linux/types.h:14:
In file included from include/uapi/linux/posix_types.h:5:
In file included from include/linux/stddef.h:5:
In file included from include/uapi/linux/stddef.h:5:
In file included from include/linux/compiler_types.h:122:
include/linux/compiler-clang.h:50:9: warning: '__HAVE_BUILTIN_BSWAP32__' macro redefined [-Wmacro-redefined]
#define __HAVE_BUILTIN_BSWAP32__
        ^
<command line>:4:9: note: previous definition is here
#define __HAVE_BUILTIN_BSWAP32__ 1
        ^
In file included from <built-in>:2:
In file included from /virtual/include/bcc/bpf.h:12:
In file included from include/linux/types.h:6:
In file included from include/uapi/linux/types.h:14:
In file included from include/uapi/linux/posix_types.h:5:
In file included from include/linux/stddef.h:5:
In file included from include/uapi/linux/stddef.h:5:
In file included from include/linux/compiler_types.h:122:
include/linux/compiler-clang.h:51:9: warning: '__HAVE_BUILTIN_BSWAP64__' macro redefined [-Wmacro-redefined]
#define __HAVE_BUILTIN_BSWAP64__
        ^
<command line>:5:9: note: previous definition is here
#define __HAVE_BUILTIN_BSWAP64__ 1
        ^
In file included from <built-in>:2:
In file included from /virtual/include/bcc/bpf.h:12:
In file included from include/linux/types.h:6:
In file included from include/uapi/linux/types.h:14:
In file included from include/uapi/linux/posix_types.h:5:
In file included from include/linux/stddef.h:5:
In file included from include/uapi/linux/stddef.h:5:
In file included from include/linux/compiler_types.h:122:
include/linux/compiler-clang.h:52:9: warning: '__HAVE_BUILTIN_BSWAP16__' macro redefined [-Wmacro-redefined]
#define __HAVE_BUILTIN_BSWAP16__
        ^
<command line>:3:9: note: previous definition is here
#define __HAVE_BUILTIN_BSWAP16__ 1
        ^
/virtual/main.c:72:21: error: incomplete definition of type 'struct request'
    info.major = req->rq_disk->major;
                 ~~~^
include/linux/blkdev.h:32:8: note: forward declaration of 'struct request'
struct request;
       ^
/virtual/main.c:73:21: error: incomplete definition of type 'struct request'
    info.minor = req->rq_disk->first_minor;
                 ~~~^
include/linux/blkdev.h:32:8: note: forward declaration of 'struct request'
struct request;
       ^
/virtual/main.c:86:26: error: incomplete definition of type 'struct request'
    info.rwflag = !!((req->cmd_flags & REQ_OP_MASK) == REQ_OP_WRITE);
                      ~~~^
include/linux/blkdev.h:32:8: note: forward declaration of 'struct request'
struct request;
       ^
/virtual/main.c:102:27: error: incomplete definition of type 'struct request'
        valp->bytes += req->__data_len;
                       ~~~^
include/linux/blkdev.h:32:8: note: forward declaration of 'struct request'
struct request;
       ^
3 warnings and 4 errors generated.
Traceback (most recent call last):
  File "/usr/sbin/./biotop-bpfcc", line 176, in <module>
    b = BPF(text=bpf_text)
  File "/usr/lib/python3/dist-packages/bcc/__init__.py", line 364, in __init__
    raise Exception("Failed to compile BPF module %s" % (src_file or "<text>"))
Exception: Failed to compile BPF module <text>
root@gpu-2:/usr/sbin
```
#### error
```log
AttributeError: /lib/x86_64-linux-gnu/libbcc.so.0: undefined symbol: bpf_module_create_b
```
#### trace_pipe error  
```
Exception has occurred: OSError       (note: full exception trace is shown but execution is paused at: _run_module_as_main)
[Errno 16] Device or resource busy: '/sys/kernel/debug/tracing/trace_pipe'
  File "/usr/lib/python3/dist-packages/bcc/__init__.py", line 1495, in trace_open
    self.tracefile = open("%s/trace_pipe" % TRACEFS, "rb")
  File "/usr/lib/python3/dist-packages/bcc/__init__.py", line 1544, in trace_readline
    trace = self.trace_open(nonblocking)
  File "/usr/lib/python3/dist-packages/bcc/__init__.py", line 1568, in trace_print
    line = self.trace_readline(nonblocking=False)
  File "/home/gpu/go/src/eBPF/bcc/examples/hello_world.py", line 12, in <module>
    BPF(text='int kprobe__sys_clone(void *ctx) { bpf_trace_printk("Hello, World!\\n"); return 0; }').trace_print()
  File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main (Current frame)
    return _run_code(code, main_globals, None,
OSError: [Errno 16] Device or resource busy: '/sys/kernel/debug/tracing/trace_pipe'
```
==>> remove  default  bpfcc-tools ==> bpfcc-tools


### Install and compile BCC
```sh
$ git clone https://github.com/iovisor/bcc.git
$ mkdir bcc/build; cd bcc/build
$ cmake ..
$ make
$ sudo make install
$ cmake -DPYTHON_CMD=python3 .. # build python3 binding
$ pushd src/python/
$ make
$ sudo make install
$ popd
```
* 혹시 남아 있는  bpf 패키지들이 있으면 지워 준다.  


### bpftool 설치 
* ~/code/eBPF/bcc/libbpf-tools/bpftool

```sh
$ git clone --recurse-submodules https://github.com/libbpf/bpftool.git
$ git submodule update --init
$ cd src
$ make
$ export  LANG=C
$ make
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  GEN      profiler.skel.h
  CC       prog.o
  CC       struct_ops.o
  CC       tracelog.o
  CC       xlated_dumper.o
  CC       disasm.o
  LINK     bpftool

$ sudo make install
[sudo] password for jhyunlee: 
...                        libbfd: [ OFF ]
...               clang-bpf-co-re: [ on  ]
...                          llvm: [ OFF ]
...                        libcap: [ OFF ]
  INSTALL  bpftool
$ bpftool

Usage: bpftool [OPTIONS] OBJECT { COMMAND | help }
       bpftool batch file FILE
       bpftool version

       OBJECT := { prog | map | link | cgroup | perf | net | feature | btf | gen | struct_ops | iter }
       OPTIONS := { {-j|--json} [{-p|--pretty}] | {-d|--debug} |
                    {-V|--version} }

$ which bpftool
/usr/local/sbin/bpftool
```