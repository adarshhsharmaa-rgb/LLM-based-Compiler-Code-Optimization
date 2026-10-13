// category: dead_code  (real program 011)
// Codeforces submission 30138444, problem 854/A, MS C++, 2017-09-06
// https://codeforces.com/contest/854/submission/30138444
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

using namespace std;
int main()
{
	int aa, bb, a, b, n, aaa, bbb, k;
	scanf("%i", &n);
	k = 0;
	for (int i = 1; i <= n / 2; i++)
	{
		a = i;
		b = n - i;
		aa = a;
		bb = b;
		while ((aa != 0) && (bb != 0))
		{
			if (aa > bb)
				aa = aa % bb;
			else
				bb = bb % aa;
		}
		if (aa + bb == 1)
		{
			aaa = a;
			bbb = b;
			k = 1;
		}
	}
	printf("%i %i", aaa, bbb);
}
