// category: dead_code  (real program 007)
// Codeforces submission 43766543, problem 1060/B, C++17 (GCC 7-32), 2018-10-04
// https://codeforces.com/contest/1060/submission/43766543
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
#define ll long long
int main(){
	ll n,nn,i,j,m=1,wei=0,ans=0;
	scanf("%I64d",&n);
	while(m<=n){
		m*=10;
	}
	m/=10;
	nn=n%m;
	m=n-nn;
	m--;
	nn++;
	while(nn){
		ans+=nn%10;
		nn/=10;
	}
	while(m){
		ans+=m%10;
		m/=10;
	}
	printf("%I64d\n",ans);
}
