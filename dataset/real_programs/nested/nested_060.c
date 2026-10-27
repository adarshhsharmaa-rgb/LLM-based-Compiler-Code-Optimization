// category: nested  (real program 060)
// Codeforces submission 20656650, problem 678/A, GNU C++, 2016-09-16
// https://codeforces.com/contest/678/submission/20656650
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main(){

	int n, k;

	scanf("%d%d", &n, &k);

	printf("%d\n", n + (k - n % k));

	return 0;

}
