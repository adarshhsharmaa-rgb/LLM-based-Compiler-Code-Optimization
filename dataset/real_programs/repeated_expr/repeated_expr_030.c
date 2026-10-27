// category: repeated_expr  (real program 030)
// Codeforces submission 14326696, problem 32/C, GNU C++, 2015-11-18
// https://codeforces.com/contest/32/submission/14326696
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main ()
{
	long long n, m, s, x;
	scanf ("%I64d%I64d%I64d", &n, &m, &s);
	x = ((m-1)%s+1)*((m-1)/s+1)*((n-1)/s+1)*((n-1)%s+1);
	printf ("%I64d\n", x);
}
