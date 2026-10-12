// category: loops  (real program 053)
// Codeforces submission 3466772, problem 46/A, GNU C++, 2013-04-03
// https://codeforces.com/contest/46/submission/3466772
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
	int i, n, cur=1;
	scanf("%d", &n);
	for (i=1; i<n; i++)
	{
		printf("%d ", cur%n+1);
		cur += (i+1);
	}
	printf("\n");
	return 0;
}
