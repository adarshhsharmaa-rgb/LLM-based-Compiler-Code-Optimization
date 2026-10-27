// category: dead_code  (real program 004)
// Codeforces submission 59997120, problem 1214/A, C++17 (GCC 7-32), 2019-09-04
// https://codeforces.com/contest/1214/submission/59997120
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long long int h,total,d,x,y,e,mi;
    scanf("%lld%lld%lld",&total,&d,&e);
    mi=total;
    long long int may=total/(5*e);
    long long int mad=total/d;

    for(x=0;x<=mad;x++)
    {
        y=(total-d*x)/(5*e);
        h=total-d*x-5*y*e;
        if(h<mi)
        {
            mi=h;
        }
    }
    printf("%lld",mi);
    return 0;
}
