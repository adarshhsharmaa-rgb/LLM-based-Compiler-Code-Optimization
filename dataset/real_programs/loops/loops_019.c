// category: loops  (real program 019)
// Codeforces submission 17113586, problem 630/L, GNU C++, 2016-04-01
// https://codeforces.com/contest/630/submission/17113586
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
    int n;
    scanf("%d", &n);
    n = n-n%10000 + n/100%10*1000 + n%10*100 + n/10%10*10 + n/1000%10;
    long long res = 1LL;
    for(int i=0; i<5; i++) res = res*n%100000;
    printf("%05lld\n", res);
    return 0;
}
