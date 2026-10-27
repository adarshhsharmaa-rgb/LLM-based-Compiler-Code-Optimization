// category: nested  (real program 031)
// Codeforces submission 19271701, problem 630/K, GNU C++, 2016-07-20
// https://codeforces.com/contest/630/submission/19271701
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#define LLU unsigned long long
int main() {
	LLU n;
	scanf("%llu",&n);
	printf("%llu\n",n-((n/2+n/3+n/5+n/7)-(n/6+n/10+n/14+n/15+n/21+n/35)+(n/30+n/42+n/70+n/105)-n/210));
}
