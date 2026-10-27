// category: mixed  (real program 025)
// Codeforces submission 7172515, problem 450/B, GNU C++, 2014-07-19
// https://codeforces.com/contest/450/submission/7172515
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<iostream>

using namespace std;

int n,m=1000000007;
long long ans,x,y;

int main(){
	scanf("%lld %lld",&x,&y);
	scanf("%d",&n);
	n=n%6;
	if(n==0) n=6;
	if(n<=2){
		if(n==1){
			ans=x%m;
			if(ans<0) ans=m+ans;
			printf("%lld\n",ans);
		}
		else{
			ans=y%m;
			if(ans<0) ans=m+ans;
			printf("%lld\n",ans);
		}
		return 0;
	}

	for(int i=3;i<=n;i++){
		ans=y-x;
		x=y;
		y=ans;
	}
	ans=ans%m;
	if(ans<0) ans=m+ans;
	printf("%lld\n",ans);
}
