// category: nested  (real program 018)
// Codeforces submission 16155783, problem 630/G, GNU C++, 2016-02-18
// https://codeforces.com/contest/630/submission/16155783
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
	int n;
	scanf("%d", &n);
	unsigned long long tmp, ans = 1;
	tmp = n;
	tmp = tmp * (n + 1) / 2;
	tmp = tmp * (n + 2) / 3;
	ans *= tmp;
	tmp = tmp * (n + 3) / 4;
	tmp = tmp * (n + 4) / 5;
	ans *= tmp;
	printf("%I64u\n", ans);
	return 0;
}
