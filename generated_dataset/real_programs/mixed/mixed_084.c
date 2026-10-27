// category: mixed  (real program 084)
// Codeforces submission 60015608, problem 1214/A, GNU C11, 2019-09-04
// https://codeforces.com/contest/1214/submission/60015608
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long long int n,d,e,t,m,min,a;
    scanf("%lld %lld %lld",&n,&d,&e);
    e*=5;
    if(d>e){t=e;e=d;d=t;}
    m=n/d;n%=d;min=n;
    for(a=1;a<=m;a++){
        if(e>n)n+=d;
        if(n>=e)n%=e;
        if(min>n)min=n;
    }
    printf("%lld\n",min);
    return 0;
}
