// category: loops  (real program 032)
// Codeforces submission 18629462, problem 630/I, GNU C++, 2016-06-21
// https://codeforces.com/contest/630/submission/18629462
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
using namespace std;
long long n,i,ans,tmp;
int main() 
{
	scanf("%I64d",&n);
	ans=0;tmp=1;
	for (i=1;i<=n-1;i++)
	{
		tmp*=4;
	}
	ans=tmp*3/2+tmp*9/16*(n-3);
	printf("%I64d\n",ans);
	return 0;
}
