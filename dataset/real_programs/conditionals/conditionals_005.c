// category: conditionals  (real program 005)
// Codeforces submission 44512539, problem 1054/A, C++17 (GCC 7-32), 2018-10-18
// https://codeforces.com/contest/1054/submission/44512539
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a1,a2,a3,a4,a5,a6,b,c,i,j,k,d,e,f,g,h;
    scanf("%d %d %d %d %d %d",&a1,&a2,&a3,&a4,&a5,&a6);
    b=(a1-a2);
    if(b<0)
    {
        b=b*(-1);
    }
    c=(b*a4);
    d=(a3-a1);
    if(d<0)
    {
        d=d*(-1);
    }
    e=(d*a5);
    f=(b*a5);
    g=(e+f)+(a6*3);
    if(g>c)
    {
        printf("NO\n");
    }
    else
    {
        printf("YES\n");
    }
    return 0;
}
