// category: dead_code  (real program 009)
// Codeforces submission 32169437, problem 888/D, C++14 (GCC 6-32), 2017-11-09
// https://codeforces.com/contest/888/submission/32169437
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
#include <cstring>
#include <algorithm>
using namespace std;
typedef long long ll;
int main() {
	ll a, b, c, d;
	int n, k, tem = 1;
	scanf("%d%d", &n, &k);
	a = 1;
	b = 1ll*n*(n-1)/2;
	c = 1ll*n*(n-1)*(n-2)/3;
	d = 1ll*n*(n-1)*(n-2)*(n-3)*3/8;
	if(k == 1)
	printf("%lld\n", a);
	if(k == 2)
	printf("%lld\n", a+b);
	if(k == 3)
	printf("%lld\n", a+b+c);
	if(k == 4)
	printf("%lld\n", a+b+c+d);
}
