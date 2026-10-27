// category: mixed  (real program 090)
// Codeforces submission 42937385, problem 1041/B, GNU C++11, 2018-09-16
// https://codeforces.com/contest/1041/submission/42937385
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

int main()
{

    long long w,h,x,y,num,x1,y1,r;

    scanf("%lld %lld %lld %lld",&w,&h,&x,&y);

    x1=x;
    y1=y;
    r=x;
    while(r!=0)
    {
        r = x1%y1;
        x1=y1;
        y1=r;
    }
    num =x1;
    x/=num;
    y/=num;

    x1 = w/x;
    y1 = h/y;
    if(x1<y1)
        num = x1;
    else
        num = y1;
    printf("%lld",num);

    return 0;
}
