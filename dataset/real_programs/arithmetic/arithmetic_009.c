// category: arithmetic  (real program 009)
// Codeforces submission 293040997, problem 2041/E, C++20 (GCC 13-64), 2024-11-24
// https://codeforces.com/contest/2041/submission/293040997
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
#define int long long
#define inf 0x3f3f3f3f3f3f3f3f


signed main(){
	int a,b;
	scanf("%lld%lld",&a,&b); 
	printf("3\n");
	a*=3;
	printf("%lld %lld ",b,b); 
	a-=2*b;
	printf("%lld",a);
	return 0;
}
