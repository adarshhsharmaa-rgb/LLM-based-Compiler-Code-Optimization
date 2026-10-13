// category: loops  (real program 054)
// Codeforces submission 43772160, problem 1060/B, GNU C11, 2018-10-04
// https://codeforces.com/contest/1060/submission/43772160
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main() {
	long long n,n2;
	int ans=0;

	scanf("%I64d", &n);
	n2 = 9;
	while (n > n2) {
		ans += 9;
		n2 *= 10;
		n2 += 9;
	}
	n2 /= 10;
	n -= n2;
	while (n > 0) {
		ans += n % 10;
		n /= 10;
	}
	printf("%d", ans);
}
