// category: nested  (real program 051)
// Codeforces submission 16780488, problem 630/K, GNU C++, 2016-03-18
// https://codeforces.com/contest/630/submission/16780488
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main()
{
	__int64 n,result;
	scanf("%I64d",&n);
	result=n-(n/2+n/3+n/5+n/7)+(n/6+n/10+n/14+n/15+n/21+n/35)-(n/30+n/42+n/70+n/105)+n/210;
	printf("%I64d\n",result);
	return 0;
}
