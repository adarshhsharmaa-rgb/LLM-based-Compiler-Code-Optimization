// category: repeated_expr  (real program 046)
// Codeforces submission 16341886, problem 219/B, GNU C++, 2016-02-26
// https://codeforces.com/contest/219/submission/16341886
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

long long p, d, ans;

int main() {
	scanf("%I64d%I64d", &p, &d);
	ans = p;
	for(long long x=10;x<=p;x*=10) {
		long long a = p/x, b = p%x;
		if(b<x-1)a--;
		if(p-d<=a*x+x-1) ans = a*x+x-1;
	}
	printf("%I64d\n", ans);
	
	return 0;
}
