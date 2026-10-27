// category: mixed  (real program 067)
// Codeforces submission 590380, problem 104/A, MS C++, 2011-08-07
// https://codeforces.com/contest/104/submission/590380
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
	int n;
	int now = 10, count = 0;
	scanf("%d", &n);
	for (int  i = 1; i <= 11; ++i)
		if (now + i == n)
			if (i == 10)
				count += 15;
			else
				count += 4;
	printf("%d\n", count);
	return 0;
}
