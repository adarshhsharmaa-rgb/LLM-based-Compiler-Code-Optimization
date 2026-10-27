// category: conditionals  (real program 019)
// Codeforces submission 7810733, problem 76/D, GNU C++, 2014-09-16
// https://codeforces.com/contest/76/submission/7810733
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstring>

int main() {
	long long A, B;
	scanf("%lld%lld", &A, &B);
	long long X = (A - B) / 2;
	long long Y = X + B;
	if (2 * X + B != A) puts("-1");
	else printf("%lld %lld\n", X, Y);
	return 0;
}
