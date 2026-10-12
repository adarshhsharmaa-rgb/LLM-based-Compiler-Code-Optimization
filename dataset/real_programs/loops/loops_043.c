// category: loops  (real program 043)
// Codeforces submission 17115721, problem 656/D, GNU C++11, 2016-04-01
// https://codeforces.com/contest/656/submission/17115721
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main(){
	int n;
	scanf("%d", &n);
	int ans = 0;
	for (; n > 0; n /= 8)
		ans += n % 8 == 1;
	printf("%d\n", ans);
	return 0;
}
