// category: repeated_expr  (real program 005)
// Codeforces submission 60015131, problem 1214/A, GNU C11, 2019-09-04
// https://codeforces.com/contest/1214/submission/60015131
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main() {
	int  n;
	scanf("%d", &n);
	int dollar, euro;
	scanf("%d", &dollar);
	scanf("%d", &euro);
	euro *= 5;
	int min = n;
	for (int i = 0; i <= n/dollar; i++) {
		if (min > (n - i * dollar) % euro){
			min = (n - i * dollar) % euro;
		}
	}
	printf("%d", min);
	return 0;

}
