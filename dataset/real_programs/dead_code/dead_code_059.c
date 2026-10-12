// category: dead_code  (real program 059)
// Codeforces submission 33337165, problem 899/C, C++14 (GCC 6-32), 2017-12-17
// https://codeforces.com/contest/899/submission/33337165
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
using namespace std;
typedef long long ll;
int main(){
	//freopen("a.in","r",stdin);
	//freopen("a.out","w",stdout);
	ll n;
	scanf("%lld",&n);
	if(n%2==0){
		ll res=n/2;
		printf("%lld\n",res%2);
		ll u=res/2;
		printf("%lld ",res);
		for(ll i=1;i<=u;i++)
			printf("%lld ",i*2);
		for(ll i=u+1;i<=res;i++)
			printf("%lld ",i*2-1);
	}
	else {
		ll res=n/2;
		ll N=res*2;
		ll tmp=res+1;
		ll u=tmp/2;
		printf("%lld\n",tmp%2);
		printf("%lld ",res);
		for(ll i=1;i<=u;i++)
			printf("%lld ",2*i+1);
		for(ll i=u+1;i<=res;i++)
			printf("%lld ",2*i);
	}
return 0;
}
