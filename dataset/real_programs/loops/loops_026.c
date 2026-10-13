// category: loops  (real program 026)
// Codeforces submission 43848997, problem 1059/C, MS C++, 2018-10-05
// https://codeforces.com/contest/1059/submission/43848997
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

using namespace std;

int main()
{
	int n;
	int left;
	int q, t;
	int base = 2;
	int i;

	scanf("%d", &n);

	left = n;

	while (n >= base * 2)
	{
		q = n / base;

		t = left - q;

		for (i = 0; i < t; i++)
		{
			printf("%d ", base / 2);
		}

		left -= t;

		base *= 2;
	}

	base /= 2;

	for (i = 0; i < left - 1; i++)
	{
		printf("%d ", base);
	}

	printf("%d", base*left);

	return 0;
}
