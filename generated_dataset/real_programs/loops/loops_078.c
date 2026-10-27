// category: loops  (real program 078)
// Codeforces submission 33687505, problem 909/B, GNU C, 2017-12-27
// https://codeforces.com/contest/909/submission/33687505
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main() {
	int n;
	scanf("%d", &n);
	short i, a = 2, b = 1;
	--n;
	for(i = 0; i < n; ++i) {
		b = a*(a+1)/2 - b;
		++a;
	}
	printf("%hd", b);
	return 0;
}
