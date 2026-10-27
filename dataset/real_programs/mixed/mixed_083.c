// category: mixed  (real program 083)
// Codeforces submission 43857043, problem 1059/C, GNU C++11, 2018-10-05
// https://codeforces.com/contest/1059/submission/43857043
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
int main()
{
    int n;
    scanf("%d",&n);
    int res=1;
    int cnt=0;
    while(n>3)
    {
        cnt=(n+1)/2;
        for(int i=0;i<cnt;i++)
            printf("%d ",res);
        res=res*2;
        n-=cnt;
    }
    if(n==1)
        printf("%d",res);
    else if(n==2)
        printf("%d %d",res,res*2);
    else
        printf("%d %d %d\n",res,res,res*3);
}
