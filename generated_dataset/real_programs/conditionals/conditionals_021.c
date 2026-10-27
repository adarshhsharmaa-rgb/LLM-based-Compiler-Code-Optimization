// category: conditionals  (real program 021)
// Codeforces submission 19005849, problem 690/A1, MS C++, 2016-07-10
// https://codeforces.com/contest/690/submission/19005849
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <algorithm>

using namespace std;

int main() {
	int N;
	scanf("%d", &N);
	int ans = N/2;
	if (N%2 != 0) ans++;
	printf("%d\n", ans);
	return 0;
}
