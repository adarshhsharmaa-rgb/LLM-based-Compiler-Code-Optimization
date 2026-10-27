// category: dead_code  (real program 053)
// Codeforces submission 39617102, problem 996/A, C++14 (GCC 6-32), 2018-06-24
// https://codeforces.com/contest/996/submission/39617102
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a=0,b=0,c=0,d=0,e=0,n,p=0,q=0,r=0,s=0,t=0,m=0;
    scanf("%d",&n);
    a=n%100;
    p=n/100;

    b=a%20;
    q=a/20;

    c=b%10;
    r=b/10;

    d=c%5;
    s=c/5;

    e=d%1;
    t=d/1;
    m=p+q+r+s+t;
    printf("%d",m);
    return 0;
}
