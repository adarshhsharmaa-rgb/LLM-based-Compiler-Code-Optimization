// category: mixed  (real program 034)
// Codeforces submission 21442058, problem 534/A, MS C++, 2016-10-15
// https://codeforces.com/contest/534/submission/21442058
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#define _CRT_SECURE_NO_WARNINGS

#include <cstdio>

#include <vector>

#include <queue>

#include <string>

#include <algorithm>

#include <iostream>

#include <cmath>

#include <map>

#include <set>

using namespace std;







int main()

{

	int n; scanf("%d", &n);

	if (n < 4&&n!=1)

	{

		printf("%d\n", n - 1);

		for (int i = 1; i <= n; i += 2)

			printf("%d ", i);

		return 0;

	}

	printf("%d\n", n);

	for (int i = 2; i <= n; i+=2)

		printf("%d ", i);

	for (int i = 1; i <= n; i += 2)

		printf("%d ", i);

}
