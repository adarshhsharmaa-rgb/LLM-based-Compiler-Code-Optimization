// category: conditionals  (real program 034)
// Codeforces submission 22236124, problem 734/B, GNU C, 2016-11-15
// https://codeforces.com/contest/734/submission/22236124
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int i,j2,j3,j5,j6,k2,k3,k5,k6,l=0,m=0,n,x;
    scanf("%d %d %d %d",&j2,&j3,&j5,&j6);

    k2=j2;
    k3=j3;
    k5=j5;
    k6=j6;

    if(k2<=k5 && k2 <=k6)
    m=k2;
    else if(k5<=k2 && k5 <=k6)
    m=k5;
    else if(k6<=k2 && k6<=k5)
    m=k6;
    l=k2-m;
    if(l<=k3)
    l=l;
    else
    l=k3;
    x=m*256+l*32;
    printf("%d\n",x);

}
