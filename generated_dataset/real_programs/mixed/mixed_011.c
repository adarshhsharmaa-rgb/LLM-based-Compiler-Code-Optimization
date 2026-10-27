// category: mixed  (real program 011)
// Codeforces submission 33685132, problem 909/B, GNU C, 2017-12-27
// https://codeforces.com/contest/909/submission/33685132
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main(void)
{
    int n,x;
    int i,sum;
    scanf("%d",&n);
    x = n;
    n = n / 2;
    sum = 0;
    for (i = 0;i <= n;i++)
        sum = sum + i;
    sum = sum * 2;
    if (x % 2 == 1)
        sum = sum + n + 1;
    printf("%d",sum);
    return 0;
}
