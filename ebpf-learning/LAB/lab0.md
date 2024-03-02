## hello 
* hello.c
```c
$ vi hello.c
#include <stdio.h>
int VAL=0;
int main(){
    for (int i=0;i<10;i++){
          printf("hello worldi [%d]\n", i);
    }
    return 0;
}
```
* factorial.c
```c
#include <stdio.h>

int factorial(int n)
{
    return (n <= 1 ? 1 : n * factorial(n - 1));
}
int N = 10;
int main(void)
{
    int n = N;
    printf("factorial(%d) = %d\n", n, factorial(n));
    return 0;
}
```

```sh
$ gcc -g -pg -o hello hello.c
$ ./hello
$ file ./hello
$ ldd  ./hello
$ hexdump -C  ./hello | head -4
$ xxd ./hello 
$ readelf -h ./hello 
$ readelf -l ./hello
$ objdump -d ./hello | more 
$ objdump -x ./hello | more 
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

## factorial

```sh
$ vi hello.c
#include <stdio.h>
int VAL=0;
int main(){
    for (int i=0;i<10;i++){
          printf("hello worldi [%d]\n", i);
    }
    return 0;
}
```

```sh
$ gcc -g -pg -o facto facto.c
$ sudo uftrace -K 5 ./hello
$ sudo uftrace record -K 5 ./hello
$ sudo uftrace tui 
```
