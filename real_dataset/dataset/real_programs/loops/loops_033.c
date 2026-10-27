// category: loops  (real program 033)
// Codeforces submission 31657036, problem 877/C, GNU C11, 2017-10-23
// https://codeforces.com/contest/877/submission/31657036
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(void)
{
	int n;
	scanf("%d", &n);

	int cnt = 0;

	for (int i = 2; i <= n; i += 2)
		cnt += 2;

	for (int i = 1; i <= n; i += 2)
		cnt ++;

	
	printf("%d\n", cnt);
	for (int i = 2; i <= n; i += 2)
		printf("%d ", i);
	for (int i = 1; i <= n; i += 2)
		printf("%d ", i);
	for (int i = 2; i <= n; i += 2)
		printf("%d ", i);
}
