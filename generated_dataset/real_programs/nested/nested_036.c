// category: nested  (real program 036)
// Codeforces submission 653328, problem 32/C, GNU C++, 2011-08-31
// https://codeforces.com/contest/32/submission/653328
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(void) {
	int n, m, s;
	scanf("%d%d%d", &n, &m, &s);
	--n;--m;
	printf("%I64d\n", (n%s+1)*1LL*(m%s+1)*(m/s+1)*(n/s+1));
	return 0;
}
