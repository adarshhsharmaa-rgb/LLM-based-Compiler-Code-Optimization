// category: loops  (real program 036)
// Codeforces submission 16902565, problem 645/B, GNU C++, 2016-03-24
// https://codeforces.com/contest/645/submission/16902565
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main()
{
	int n,k;
	scanf("%d%d",&n,&k);
	long long ans=0;
	for(int i=0;i<k&&i<n/2;i++)
		ans+=2*n-4*i-3;
	printf("%I64d\n",ans);
	return 0;
}
