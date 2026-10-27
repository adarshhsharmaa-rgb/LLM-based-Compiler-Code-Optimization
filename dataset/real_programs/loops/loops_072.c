// category: loops  (real program 072)
// Codeforces submission 3377759, problem 285/A, GNU C++, 2013-03-22
// https://codeforces.com/contest/285/submission/3377759
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
	int n,k,i;
	scanf("%d%d", &n, &k);
	for(i=1;i<=n-(k+1);i++) printf("%d ",i);
	for(i=n;i>=n-k;i--) printf("%d ",i);
	printf("\n");
}
