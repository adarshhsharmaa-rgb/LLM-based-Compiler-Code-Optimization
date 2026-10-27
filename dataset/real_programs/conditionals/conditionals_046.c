// category: conditionals  (real program 046)
// Codeforces submission 41718558, problem 1023/B, GNU C++, 2018-08-17
// https://codeforces.com/contest/1023/submission/41718558
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
long long n,m,x;
int main(){
	scanf("%lld%lld",&n,&m);
	if(m<=n){
		printf("%lld",(m-1)/2);
	}
	else{
		if(2*n>m){
			x=m-n;
			x=(n-x+1);
			printf("%lld\n",x/2);
		}
		else printf("0\n");
	}
}
