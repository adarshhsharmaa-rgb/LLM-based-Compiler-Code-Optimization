// category: mixed  (real program 079)
// Codeforces submission 16254447, problem 630/F, GNU C++, 2016-02-21
// https://codeforces.com/contest/630/submission/16254447
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main() {
	int n;
	long long mul = 1, sum = 0;
	scanf("%d", &n);
	for(int i=1; i<=7; ++i)
	{
		mul *= n-i+1;
		mul /= i;
		if(i>=5) sum += mul;
	}
	printf("%I64d\n", sum);
	return 0;
}
