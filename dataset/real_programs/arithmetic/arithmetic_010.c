// category: arithmetic  (real program 010)
// Codeforces submission 5853540, problem 387/A, GNU C++, 2014-01-31
// https://codeforces.com/contest/387/submission/5853540
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main()
{
	int a,b,c,d,e,f;
	scanf("%d:%d%d:%d",&a,&b,&c,&d);
	a+=24*(a<c||(a==c&&b<d));
	f=b-d+60*(b<d);
	e=a-c-(b<d);
	printf("%02d:%02d",e,f);
}
