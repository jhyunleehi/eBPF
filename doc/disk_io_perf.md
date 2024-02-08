# IO 측정과 모니터링
## 성능 측정

### 1.  fio 

```sh
fio --name=randrw --ioengine=libaio --direct=1 --rw=randrw --size=1G --runtime=60 --time_based --group_reporting
fio --name=random_rw_test --ioengine=libaio --direct=1 --rw=randrw --bs=4k --size=1G --runtime=60 --filename=/dev/sdx
fio --name=seq_io_test --ioengine=libaio --rw=write --bs=1M --size=1G --direct=1 --filename=./testfile --runtime=60
fio --name=seq_io_test --ioengine=libaio --rw=readwrite --bs=1M --size=1G --direct=1 --filename=./testfile --runtime=60
```

- name=randrw: Specifies the name of the job.
- ioengine=libaio: Sets the I/O engine to use. In this case, it's libaio (Linux asynchronous I/O).
- direct=1: Enables direct I/O, bypassing the operating system cache.
- rw=randrw: Specifies that the workload should be a mix of random reads and writes.
- rw=randrw. If you're interested in testing sequential read and write performance separately
- rw=read or --rw=write
    - read: Performs a sequential read workload.
    - write: Performs a sequential write workload.
    - randread: Performs random reads within the file.
    - randwrite: Performs random writes within the file.
    - randrw: Performs a mix of random reads and writes.
    - readwrite: Performs a mix of sequential reads and writes.
- size=1G: Sets the size of the test file to 1 gigabyte.
- runtime=60: Specifies the duration of the test in seconds. In this example, it runs for 60 seconds.
- time_based: Indicates that the test duration is time-based (as opposed to specifying a specific number of I/O operations).
- group_reporting: Enables group reporting, which aggregates results across all threads.

### 2. dd
* dd 명령에서 direct가 맞았나?

```sh
$ dd if=/dev/sda of=/dev/sdb bs=4k iflag=direct oflag=direct
$ dd if=/dev/zero of=./f1 bs=4K iflag=direct oflag=direct
$ dd if=/dev/urandom  of=./f1 bs=1M count=1000 iflag=direct oflag=direct

$ while true; do dd if=/dev/zero of=./f1 bs=1M count=1000  oflag=direct; done

```
- bs=4k: Specifies the block size. You can adjust it as needed.
- iflag=direct: Enables direct I/O for the input file/device.
- oflag=direct: Enables direct I/O for the output file/device.

### 3. iozone
* 파일 시스템 성능 측정도구 
* [https://www.iozone.org/](https://www.iozone.org/)
* [참고](https://ji007.tistory.com/entry/IOzone-Option)
```sh
$ sudo apt update
$ sudo apt install iozone3
$ iozone -a        //automatic mode 그냥 간단히 실행하는 거다
$ iozone -Ra       // 그래프를 그리기위해서(Excel) R을 추가한다
$ iozone -Ra -g -2G // 사용시스템이 512Mbyte이상 메모리일경우 지정해준다
$ iozone -Ra -g 2G -i 0 -i 1    //-i후에 각 해당되는 번호(뒤에 설명)를 붙여주면 해당 peration만 test한다. 여기서 0은 write, 1은 read다
$ iozone  -Rac     //NFS에서 test시에 유용한 옵션 (-c)
```
### 4. hdparm

```sh
$ hdparm -Tt /dev/sda
$ hdparm -Tt /dev/nvme0n1

$ sudo hdparm -Tt /dev/nvme0n1
/dev/nvme0n1:
 Timing cached reads:   35618 MB in  1.97 seconds = 18034.84 MB/sec
 Timing buffered disk reads: 2338 MB in  3.00 seconds = 778.75 MB/sec
```

#### 5. sysbench
* cpu, memory, disk 성능  측정
```sh
$ apt install sysbench
$ sysbench fileio help
fileio options:
  --file-num=N                  number of files to create [128]
  --file-block-size=N           block size to use in all IO operations [16384]
  --file-total-size=SIZE        total size of files to create [2G]
  --file-test-mode=STRING       test mode {seqwr, seqrewr, seqrd, rndrd, rndwr, rndrw}
  --file-io-mode=STRING         file operations mode {sync,async,mmap} [sync]
  --file-async-backlog=N        number of asynchronous operatons to queue per thread [128]
  --file-extra-flags=[LIST,...] list of additional flags to use to open files {sync,dsync,direct} []
  --file-fsync-freq=N           do fsync() after this number of requests (0 - don't use fsync()) [100]
  --file-fsync-all[=on|off]     do fsync() after each write operation [off]
  --file-fsync-end[=on|off]     do fsync() at the end of test [on]
  --file-fsync-mode=STRING      which method to use for synchronization {fsync, fdatasync} [fsync]
  --file-merged-requests=N      merge at most this number of IO requests if possible (0 - don't merge) [0]
  --file-rw-ratio=N             reads/writes ratio for combined test [1.5]

$ sysbench fileio --file-total-size=1G prepare
$ sysbench fileio --file-total-size=1G --file-test-mode=seqrd run
```
* 이렇게 한짝으로 동작
```sh
$ sysbench fileio --file-test-mode=rndrw  --file-rw-ratio=2 prepare
$ sysbench fileio --file-test-mode=rndrw  --file-rw-ratio=2 run

sysbench 1.0.20 (using system LuaJIT 2.1.0-beta3)

Running the test with following options:
Number of threads: 1
Initializing random number generator from current time


Extra file open flags: (none)
128 files, 16MiB each
2GiB total file size
Block size 16KiB
Number of IO requests: 0
Read/Write ratio for combined random IO test: 2.00
Periodic FSYNC enabled, calling fsync() each 100 requests.
Calling fsync() at the end of test, Enabled.
Using synchronous I/O mode
Doing random r/w test
Initializing worker threads...

Threads started!


File operations:
    reads/s:                      280.20
    writes/s:                     140.05
    fsyncs/s:                     542.51

Throughput:
    read, MiB/s:                  4.38
    written, MiB/s:               2.19

General statistics:
    total time:                          10.2310s
    total number of events:              9723

Latency (ms):
         min:                                    0.00
         avg:                                    1.03
         max:                                    5.93
         95th percentile:                        2.11
         sum:                                 9970.43

Threads fairness:
    events (avg/stddev):           9723.0000/0.00
    execution time (avg/stddev):   9.9704/0.00

```



## 모니터링 

#### 1. # iostat -xm 1 /dev/nvme0n1
* iostat: iostat is a command-line tool that reports CPU utilization and I/O statistics for devices, partitions, and NFS. 
* 실시간으로 IO 발생하는 대역폭과 history를 그래프로 표시함. 
```sh
$ sudo apt update
$ apt install iotop-c
```

```sh
root@good:~# iostat -xm 1 /dev/nvme0n1
Linux 6.5.0-15-generic (good) 	2024년 02월 08일 	_x86_64_	(16 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
          20.41    0.01    9.71    0.18    0.00   69.69

Device            r/s     rMB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wMB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dMB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
nvme0n1          6.27      0.08     0.06   1.01    0.38    12.96   42.18      0.21     5.22  11.01    0.88     5.04    0.09      0.89     0.00   0.00    1.72 10145.35   15.79    1.96    0.07   4.47
```

### 2. iotop
* iotop: iotop is a tool that monitors I/O usage information in real-time. 
```
$ sudo apt update
$ sudo apt install iotop
$ sudo iotop
```
### 3. sar -d 
* sar: The sar command is used to collect, report, or save system activity information such as CPU, memory, network, and I/O statistics. 
```sh
$ sudo apt update
$ sudo apt install sysstat
$ sar -d  1 --dev=nvme0n1
```

#### 4.  dstat -cdn

* dstat: dstat is a versatile tool for generating system resource statistics. 
```sh
$ sudo apt update
$ sudo apt install dstat
```

```sh
--total-cpu-usage-- -dsk/total- -net/total-
usr sys idl wai stl| read  writ| recv  send
  4   3  93   0   0|  59M   61M|   0     0 
  2   3  95   0   0|  60M   60M| 321B 1372B
  2   4  94   0   0|  61M   62M|1369k   11k
  2   3  96   0   0|  60M   61M| 132B  132B
  2   3  95   0   0|  56M   56M|   0     0 
  2   3  95   0   0|  60M   61M|   0     0 
  2   3  96   0   0|  59M   59M|   0     0 
  6   5  89   0   0|  61M   61M|1392k   10
  ```



