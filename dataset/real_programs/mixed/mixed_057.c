// category: mixed  (real program 057)
// Codeforces submission 60012718, problem 1214/B, GNU C++11, 2019-09-04
// https://codeforces.com/contest/1214/submission/60012718
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
#include<cstring>
#include<cmath>
#include<algorithm>
#include<vector>
#include<queue>
#define IL inline
using namespace std;

	int b,g,n;

int main(){
	scanf("%d%d%d",&b,&g,&n);
	
	int ans=0;
	for(int i=0;i<=n;i++)
	if(b>=i&&g>=n-i)
		ans++;
	
	printf("%d",ans);

	return 0;

}
