// category: mixed  (real program 051)
// Codeforces submission 44631741, problem 1031/A, C++17 (GCC 7-32), 2018-10-21
// https://codeforces.com/contest/1031/submission/44631741
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    int i,j,w,h,n,k,big,sm,sumb=0,sums=0;
    scanf("%d %d %d",&w,&h,&k);
    if(w>h)
        {big=w;
        sm=h-2;}
    else
    {
        big=h;
        sm=w-2;
    }
    for(i=k;i>0;i--)
    {
        if(sm>0 && big>=0)
        {
            sumb+=2*big;
            sums+=2*sm;
            big-=4;
            sm-=4;
        }
    }
    printf("%d\n",sumb+sums);
    return 0;
}
