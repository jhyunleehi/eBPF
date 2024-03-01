# libbpf

https://github.com/libbpf/libbpf

Libbpf 신뢰할 수 있는 소스 코드는 linutools/lib/bpf 정기적으로 Github에 동기화됩니다. 
libbpf git 위치:  git://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git

### Libbpf 개발 참고 

* libbpf를 사용하여 BPF 애플리케이션을 구축하는 예는 libbpf-bootstrap 및  블로그 참고
* bcc아래에 있는  libbpf-tools는 실제 libbpf 좋은 예제
* BPF CO-RE 애플리케이션 구축의 실제적인 측면에 대한 내용은 "BPF CO-RE 참조 가이드"를 참조
* BPF 이식성 문제 및 BPF CO-RE 출처에 대한 일반적인 소개는 "BPF CO-RE"를 참조하세요.

* [LIBBPF API](https://libbpf.readthedocs.io/en/latest/api.html)
* [libbpf-bootstrap: demo BPF applications](https://github.com/libbpf/libbpf-bootstrap)
* [Building BPF applications with libbpf-bootstrap](https://nakryiko.com/posts/libbpf-bootstrap/)
* [BPF CO-RE reference guide](https://nakryiko.com/posts/bpf-core-reference-guide/)

* [BPF CO-RE (Compile Once – Run Everywhere)](https://nakryiko.com/posts/bpf-portability-and-co-re/)


* [BPF Portability and CO-RE](https://facebookmicrosites.github.io/bpf/blog/2020/02/19/bpf-portability-and-co-re.html)
* [HOWTO: BCC to libbpf conversion](https://facebookmicrosites.github.io/bpf/blog/2020/02/20/bcc-to-libbpf-howto-guide.html)
* [Tips & tricks for writing libbpf-tools](https://en.pingcap.com/blog/tips-and-tricks-for-writing-linux-bpf-applications-with-libbpf)


## [eBPF] CO-RE (Compile Once - Run Everywhere) 기능 분석

최근 몇 년간 리눅스 커널 커뮤니티에서 가장 주목받고 있는 기술은 누가 뭐래도 eBPF 일 것이다. 리눅스 커널에 안정성과 확장성, 그리고 생산성을 동시에 부여하는 혁신적인 기술로, 대표적인 쿠버네티스의 CNI 인 Cilium과 Falco, Pixie 등 다양한 오픈소스 프로젝트의 기반 기술로 이미 자리잡고 있으며, 점점 더 활용분야를 넓혀나가고 있다. 

### 왜 CO-RE가 필요한가?
아래 코드는 bcc 의 runqslower 예제코드 중 일부이다. 아래 함수는 리눅스 커널에서 문맥전환(context-switching)이 일어날때 실행되는 trace_sched_switch() 함수에서 호출되는 BPF 함수이다. (섹션 이름인 tp_btf/sched_switch 가 sched_switch 트레이스포인트에 해당 함수를 추가하라는 의미이다.)
* BPF_PROG는 macro이고, static sched_switch 함수 생성한다. 

* 파일의 위치 
    - hyunlee@Good:~/code$ find | grep runqslower.bpf.c
    - ./linux/tools/bpf/runqslower/runqslower.bpf.c
    - ./bcc/libbpf-tools/runqslower.bpf.c
* 컴파일 준비
```
$ cd  LAB-libbps
$ sudo cp  ~/code/eBPF/bcc/libbpf-tools/bpftool/src/vmlinux.h  /usr/include/
$ cp  ~/code/eBPF/bcc/libbpf-tools/core_fixes.bpf.h  .
$ cp  ~/code/eBPF/bcc/libbpf-tools/trace_helpers.h   .
$ bpftool gen subskeleton runqslower.bpf.o > runqslower.skel.h
$ 
```
- "$@" 또는 "$(@)"는 바로 Target 을 말합니다. 
- "$<"는 열거된 Depend중에 가장 왼쪽에 기술된 1개의 Depend를 말하며 "$^"는 Depend 전체를 
- ${Q}는 특수문제 억제하기 위해서 사용 


```c
SEC("tp_btf/sched_switch")
int BPF_PROG(sched_switch, bool preempt, struct task_struct *prev, struct task_struct *next)
{
	return handle_switch(ctx, prev, next);
}


static int handle_switch(void *ctx, struct task_struct *prev, struct task_struct *next)
{
	struct event event = {};
	u64 *tsp, delta_us;
	u32 pid;

	/* ivcsw: treat like an enqueue event and store timestamp */
	if (get_task_state(prev) == TASK_RUNNING)
		trace_enqueue(BPF_CORE_READ(prev, tgid), BPF_CORE_READ(prev, pid));

	pid = BPF_CORE_READ(next, pid);

	/* fetch timestamp and calculate delta */
	tsp = bpf_map_lookup_elem(&start, &pid);
	if (!tsp)
		return 0;   /* missed enqueue */

	delta_us = (bpf_ktime_get_ns() - *tsp) / 1000;
	if (min_us && delta_us <= min_us)
		return 0;

	event.pid = pid;
	event.prev_pid = BPF_CORE_READ(prev, pid);
	event.delta_us = delta_us;
	bpf_probe_read_kernel_str(&event.task, sizeof(event.task), next->comm);
	bpf_probe_read_kernel_str(&event.prev_task, sizeof(event.prev_task), prev->comm);

	/* output */
	bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
			      &event, sizeof(event));

	bpf_map_delete_elem(&start, &pid);
	return 0;
}

#define BPF_PROG(name, args...)						    \
..
____##name(unsigned long long *ctx, ##args)

```

