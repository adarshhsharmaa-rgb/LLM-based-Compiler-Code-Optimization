// category: loops  (real program 006)
// Codeforces submission 42366879, problem 1037/A, C++17 (GCC 7-32), 2018-09-02
// https://codeforces.com/contest/1037/submission/42366879
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

int main() {
	int n;
	scanf("%d", &n);
	
	int x = 1, ans = 0;
	while(n>0) {
		ans++;
		n-=x;
		x*=2;
	}
	printf("%d\n", ans);
	
	return 0;
}
