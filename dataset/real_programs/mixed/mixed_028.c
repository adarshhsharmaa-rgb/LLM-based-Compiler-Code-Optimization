// category: mixed  (real program 028)
// Codeforces submission 44803827, problem 1068/B, GNU C++11, 2018-10-24
// https://codeforces.com/contest/1068/submission/44803827
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    long long b,i,cnt=0;
    scanf("%lld",&b);
    for(i=1;i*i<=b;i++)
    {
        if(b%i==0)
        {
            if(b/i==i)
                cnt++;
            else
                cnt+=2;
        }
    }
    printf("%lld\n",cnt);
    return 0;
}
