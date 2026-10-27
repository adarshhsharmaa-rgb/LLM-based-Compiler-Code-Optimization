// category: dead_code  (real program 049)
// Codeforces submission 44800029, problem 1068/A, C++14 (GCC 6-32), 2018-10-24
// https://codeforces.com/contest/1068/submission/44800029
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
#define P(X) cout<<"db "<<X<<endl;
#define P2(X,Y) cout<<"d2 "<<X<<" "<<Y<<endl;
#define ll long long
#define rep(i,n) for(i=1;i<=n;i++)
#define FO freopen("t.txt","w",stdout);
#define MS(XX,YY) memset(XX,YY,sizeof(XX));
#define pii pair<int,int>
using namespace std;

int main()
{
    ll i,j,a,b,ts,f=1,cn=0,n,m,k,l,c,s;
    //freopen("test.txt","r",stdin);
    scanf("%lld %lld %lld %lld",&n,&m,&k,&l);
    //c=ceil(((long double)l+k)/m)+.00001;
    s=l+k;
    c=s/m;
    if(s%m)c++;
    if(c*m>n){
        puts("-1");
        return 0;
    }
        printf("%lld\n",c);
    return 0;
}
