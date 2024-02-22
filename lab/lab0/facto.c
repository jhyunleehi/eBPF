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