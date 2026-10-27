// category: conditionals  (real program 059)
// Codeforces submission 21975218, problem 104/A, GNU C++11, 2016-11-01
// https://codeforces.com/contest/104/submission/21975218
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

int main(void) {
	int n;
	scanf("%d", &n);
	int ans, x = n - 10;
	if(x <= 0 || x > 11) {
		ans = 0;
	} else if(x == 10) {
		ans = 15;
	} else {
		ans = 4;
	}
	printf("%d\n", ans);
	return 0;
}
