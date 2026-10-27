// category: nested  (real program 006)
// Codeforces submission 19272878, problem 630/K, GNU C++, 2016-07-20
// https://codeforces.com/contest/630/submission/19272878
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(){
	long long n, con=0;
	scanf("%lld",&n);
	con=n-(n/2+n/3+n/5+n/7-n/6-n/10-n/14-n/15-n/21-n/35+n/105+n/70+n/42+n/30-n/210);
	printf("%lld\n",con);
	return 0;
}
