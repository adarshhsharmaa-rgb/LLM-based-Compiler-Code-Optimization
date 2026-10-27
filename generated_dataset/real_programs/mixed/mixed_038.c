// category: mixed  (real program 038)
// Codeforces submission 18418620, problem 678/A, GNU C++11, 2016-06-13
// https://codeforces.com/contest/678/submission/18418620
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <algorithm>
#include <vector>

using namespace std;

int main(){
	long long n, k;
	scanf("%lld%lld", &n, &k);
	long long l = 0LL, d = 2000000001LL, mid, ans = 0LL;

	while(l <= d){
		mid = (l + d) / 2;
		if(k * mid > n){
			ans = mid;
			d = mid - 1;
		}
		else l = mid + 1;
	}

	printf("%lld\n", k * ans);
	return 0;
}
