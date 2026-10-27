// category: loops  (real program 028)
// Codeforces submission 32872882, problem 897/B, GNU C++11, 2017-12-02
// https://codeforces.com/contest/897/submission/32872882
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

int main()
{
    long long a;
    /*long long ten[20];
    ten[0]=1;
    for(int i=1;i<=18;i++)
        ten[i]=10*ten[i-1];*/
    int k,p;
    scanf("%d%d",&k,&p);
    long long ans=0;
    for(int i=1;i<=k;i++)
    {
        a=i;
        int b=a;
        while(b)
        {
            a=a*10;
            a+=(b%10);
            b/=10;
        }
        ans=(ans+a)%p;
    }
    printf("%lld\n",ans);
}
