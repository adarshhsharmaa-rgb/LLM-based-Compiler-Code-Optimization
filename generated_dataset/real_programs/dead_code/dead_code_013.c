// category: dead_code  (real program 013)
// Codeforces submission 59993768, problem 1214/B, C++14 (GCC 6-32), 2019-09-04
// https://codeforces.com/contest/1214/submission/59993768
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
/*************************************************************************
	> File Name: 2019_9_4_2.cpp
	> Author: z472421519
	> Mail: 
	> Created Time: 2019年09月04日 星期三 17时21分12秒
 ************************************************************************/

#include <bits/stdc++.h>
#include <cstdio>
#include <cstring>
using namespace std;

int main()
{
    int b,n,g;
    scanf("%d%d%d",&b,&g,&n);
    int now = 0,res,ans;
    /*
    for(int i = 0;i <= n;i++)
    {
        //printf()
        now += n - i;
        //printf("%d %d\n",now,(i + 1) * n - now);
        if(now > b)
            res = max(b,i * (i + 1) / 2);
        //printf("%d %d\n",(i + 1) * n,res);
        if((i + 1) * n - res >= g)
        {
            ans = i + 1;
            break;
        }
    }*/
    ans = 0;
    for(int i = 0;i <= n;i++)
    {
        if(i <= b && n - i <= g)
            ans++;
        //printf("%d %d\n",i,b - i);
    }
    printf("%d\n",ans);
    return 0;
}
