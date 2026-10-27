// category: dead_code  (real program 039)
// Codeforces submission 25515895, problem 785/C, C++14 (GCC 6-32), 2017-03-15
// https://codeforces.com/contest/785/submission/25515895
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<algorithm>

using namespace std;
typedef long long ll;

int main()
{
	ll n, m; scanf("%lld %lld", &n, &m);
	ll count = m;
	ll temp = n;
	if(m > n) 
	{
		printf("%lld\n", n);
		return 0;
	}
	n -= m;
	ll kir = 0, kan = 1500000000;
	while(kir != kan)
	{
		ll mid = (kir+kan)/2;
	//	printf("%lld %lld %lld\n", kir, kan, mid*(mid+1)/2);
		if(mid*(mid+1)/2 < n) kir = mid+1;
		else kan = mid;
	}
	printf("%lld\n", count+kir);
}
