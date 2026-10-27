// category: mixed  (real program 037)
// Codeforces submission 39564728, problem 991/C, C++14 (GCC 6-32), 2018-06-23
// https://codeforces.com/contest/991/submission/39564728
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
typedef long long LL;

int main()
{
    LL n,mn=999999999999999999;
    scanf("%lld",&n);
    LL half=(n+1)/2;
    LL l=1,r=n,mid;
    
    while(l<=r)
    {
        mid=(l+r)/2;
        LL temp=n,tot=0;
        while(temp)
        {
            if(mid<=temp)
            {
                tot+=mid;
                temp-=mid;
            }
            else
            {
                tot+=temp;
                temp=0;
            }
            
            temp-=(temp/10);
        }
        
        if(tot<half)
        {
            l=mid+1;
        }
        
        else
        {
            if(mid<mn)
            {
                mn=mid;
            }
            r=mid-1;
        }
    }
    
    printf("%lld\n",mn);
}
