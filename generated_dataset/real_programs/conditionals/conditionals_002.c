// category: conditionals  (real program 002)
// Codeforces submission 42632290, problem 1036/A, C++17 (GCC 7-32), 2018-09-07
// https://codeforces.com/contest/1036/submission/42632290
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main()
{
	unsigned long long k, n;
	scanf("%llu%llu", &n, &k);
	unsigned long long h = k / n;
	if(h * n < k) h ++;
	printf("%llu\n", h);
	return 0;
}
