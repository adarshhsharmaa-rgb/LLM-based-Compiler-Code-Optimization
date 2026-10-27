// category: mixed  (real program 076)
// Codeforces submission 659494, problem 112/B, GNU C++, 2011-09-03
// https://codeforces.com/contest/112/submission/659494
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
	int tn, n, x, y;
	scanf("%d %d %d\n", &tn, &x, &y);
	n = tn / 2;

	for (int i = 0; i < 2; ++i)
	for (int j = 0; j < 2; ++j) {
		int s = n + i, t = n + j;
		if (x == s && y == t) {
			puts("NO");
			return 0;
		}
	}
	puts("YES");
	return 0;
}
