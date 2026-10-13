// category: conditionals  (real program 054)
// Codeforces submission 49697340, problem 1114/A, C++17 (GCC 7-32), 2019-02-10
// https://codeforces.com/contest/1114/submission/49697340
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main() {
	int x, y, z, a, b, c;
	scanf("%d%d%d%d%d%d", &x, &y, &z, &a, &b, &c);
	if (x > a) {
		puts("NO");
		return 0;
	}
	a -= x;
	b += a;
	if (y > b) {
		puts("NO");
		return 0;
	}
	b -= y;
	c += b;
	if (z > c) {
		puts("NO");
		return 0;
	}
	puts("YES");
}
