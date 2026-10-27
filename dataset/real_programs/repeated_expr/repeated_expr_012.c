// category: repeated_expr  (real program 012)
// Codeforces submission 32174446, problem 888/D, C++14 (GCC 6-32), 2017-11-09
// https://codeforces.com/contest/888/submission/32174446
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

long long n, k, ans = 1;

int main() {

	scanf("%lld %lld", &n, &k);

	if(k >= 2) ans += n * (n - 1) / 2;
	if(k >= 3) ans += 2 * n * (n - 1) * (n - 2) / 6;
	if(k >= 4) ans += 9 * n * (n - 1) * (n - 2) * (n - 3) / 24;

	printf("%lld\n", ans);

}
