// category: mixed  (real program 068)
// Codeforces submission 835235, problem 86/A, GNU C++, 2011-11-04
// https://codeforces.com/contest/86/submission/835235
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<cstring>
#include<algorithm>
using namespace std;
int main(void)
{
	int l,r;
	scanf("%d%d", &l,&r);
	long long t=10;
	while ( r/t ) t*=10;
	long long k = t/2;
	t--;
	if ( k>r )k=r;
	else if ( k<l ) k=l;
	printf("%I64d\n", k*(t-k));
	return 0;
}
