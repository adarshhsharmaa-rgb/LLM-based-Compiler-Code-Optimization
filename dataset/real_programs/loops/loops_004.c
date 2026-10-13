// category: loops  (real program 004)
// Codeforces submission 16421551, problem 630/F, GNU C++, 2016-02-29
// https://codeforces.com/contest/630/submission/16421551
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

int n;
long long t, ans;

int main() {
	scanf("%d", &n);
	t = 1LL;
	for(int i=n-4;i<=n;i++) t*=i;
	t/=120;
	ans+=t;
	t=t*(n-5)/6;
	ans+=t;
	t=t*(n-6)/7;
	ans+=t;
	printf("%I64d\n", ans);
	
	return 0;
}
