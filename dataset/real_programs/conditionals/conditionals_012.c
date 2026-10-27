// category: conditionals  (real program 012)
// Codeforces submission 33678260, problem 909/B, GNU C++11, 2017-12-27
// https://codeforces.com/contest/909/submission/33678260
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main(){
	int n;
	scanf("%d",&n);
	int ans=0;
	if(n%2==1) ans=n/2+1;
	n/=2;
	ans+=n*(n+1);
	printf("%d\n",ans);
}
