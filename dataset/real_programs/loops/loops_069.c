// category: loops  (real program 069)
// Codeforces submission 43847085, problem 1059/C, C++14 (GCC 6-32), 2018-10-05
// https://codeforces.com/contest/1059/submission/43847085
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
	int n; scanf("%d", &n);
	int pre = 1;
	for(int i = 0; i < n; i++) {
		int cur = pre;
		while(n / (cur + pre) >= n - i) cur += pre;
		printf("%d ", cur);
		pre = cur;
	}
	printf("\n");
	return 0;
}
