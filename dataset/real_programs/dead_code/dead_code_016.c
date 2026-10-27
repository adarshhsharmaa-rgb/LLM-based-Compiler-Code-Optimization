// category: dead_code  (real program 016)
// Codeforces submission 35708498, problem 937/C, C++14 (GCC 6-32), 2018-02-25
// https://codeforces.com/contest/937/submission/35708498
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
#define max(x,y) (x)>(y)?(x):(y)
#define min(x,y) (x)<(y)?(x):(y)
const int INF = 0x3f3f3f3f;
const int MAXN=INF;
int main()
{
    long long k,d,t;
    scanf("%I64d%I64d%I64d",&k,&d,&t);
    long long round=(k/d+!!(k%d))*d;
    long long temp=k+round;
    long long ans1=2*t/temp*temp;
    long long ans2=(2*t-ans1);

    if(ans2>2*k)
    {
        ans2=2*k+(ans2-2*k)*2;
    }
    //cout<<ans1<<" "<<ans2<<endl;
    long long ans=ans1/temp*round*2+ans2;
    if(ans%2==0)
        printf("%I64d.0\n",ans/2);
    else
        printf("%I64d.5\n",ans/2);
    return 0;
}
