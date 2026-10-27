// category: mixed  (real program 053)
// Codeforces submission 43778370, problem 1060/B, GNU C++11, 2018-10-04
// https://codeforces.com/contest/1060/submission/43778370
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<algorithm>
using namespace std;

//#define scanf scanf_s

int main() {
	long long n;
	scanf("%lld", &n);
	long long t = n;
	int cnt = 0;
	int num = 0;
	if (n == 0) {
		printf("0");
		return 0;
	}
	while (n) {
		num += n % 10;
		n /= 10;
		cnt++;
	}
	cnt--;
	while (t % 10 == 9 && t >= 10) {
		cnt--;
		t /= 10;
	}
	printf("%d", num + 9 * cnt);
	return 0;
}
