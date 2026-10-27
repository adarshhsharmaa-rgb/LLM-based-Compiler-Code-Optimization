// category: nested  (real program 059)
// Codeforces submission 44626067, problem 1031/A, GNU C++11, 2018-10-21
// https://codeforces.com/contest/1031/submission/44626067
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
using namespace std;

int n,m,k;

int main()
{
	scanf("%d%d%d",&n,&m,&k);
	int a1=2*(n+m-2)*k,a2=k*(k-1)*8;
	printf("%d",a1-a2);
	return 0;
}
