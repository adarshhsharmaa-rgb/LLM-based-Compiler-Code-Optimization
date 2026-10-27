// category: nested  (real program 033)
// Codeforces submission 15234085, problem 195/A, GNU C++, 2016-01-08
// https://codeforces.com/contest/195/submission/15234085
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

int a, b, c;

int main() {
	scanf("%d%d%d", &a, &b, &c);
	printf("%d\n", (a*c-1)/b+1-c);
	
	return 0;
}
