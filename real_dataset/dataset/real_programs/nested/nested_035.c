// category: nested  (real program 035)
// Codeforces submission 16223139, problem 630/F, GNU C++, 2016-02-20
// https://codeforces.com/contest/630/submission/16223139
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
int main() {
	 long long n;
	 scanf("%I64d",&n);
	 printf("%I64d",((n*n-4*n+37)*((n*(n-1)*(n-2)*(n-3)*(n-4))/120))/42);


	return 0;
}
