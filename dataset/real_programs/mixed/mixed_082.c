// category: mixed  (real program 082)
// Codeforces submission 15053516, problem 610/A, GNU C++, 2015-12-27
// https://codeforces.com/contest/610/submission/15053516
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main () {
	long long n;
	scanf("%I64d", &n);
	if (n % 2 != 0) {
		printf("%d\n", 0);
		return 0;
	}
	int sum = 0, tmp = n / 2;
	n /= 2;
	for (int i = 1; i <= tmp / 2; i++) {
		int a = i, b = n - i;
		if (a != b) sum += 1;
	}
	printf("%d\n", sum);
	return 0;
}
