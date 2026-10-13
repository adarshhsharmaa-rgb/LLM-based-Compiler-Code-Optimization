// category: dead_code  (real program 042)
// Codeforces submission 17494334, problem 669/A, GNU C11, 2016-04-24
// https://codeforces.com/contest/669/submission/17494334
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long long int n,i,count=0;
    scanf("%lld",&n);
    if(n==1)
        printf("1");
    else if(n==2)
        printf("1");
    else if(n==3)
        printf("2");
    else
    {
        long long int n2,div,mod,m;
        n2=n;
        div=n2/3;
        mod=n2%3;
        if(mod==1||mod==2)
        m=div*2+1;
        else
           m=div*2;
        printf("%lld",m);
    }
    return 0;
}
