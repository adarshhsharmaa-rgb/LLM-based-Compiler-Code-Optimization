// category: nested  (real program 009)
// Codeforces submission 7740350, problem 379/A, GNU C++, 2014-09-11
// https://codeforces.com/contest/379/submission/7740350
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main(){
	int a, b;
	scanf("%d%d", &a, &b);
	printf("%d", a+(a-1)/(b-1));
}
