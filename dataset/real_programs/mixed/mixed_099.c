// category: mixed  (real program 099)
// Codeforces submission 33684101, problem 909/B, GNU C++11, 2017-12-27
// https://codeforces.com/contest/909/submission/33684101
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main()
{
	int n,i,l,cnt=0;
	scanf("%d",&n);
	l=n/2;
	for(i=1;i<=l;i++)
		cnt+=i;
		cnt*=2;
	if(n%2==1)
		cnt+=i;
	printf("%d\n",cnt);
	return 0;
}
