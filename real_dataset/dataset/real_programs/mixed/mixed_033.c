// category: mixed  (real program 033)
// Codeforces submission 4270090, problem 92/A, GNU C++, 2013-08-12
// https://codeforces.com/contest/92/submission/4270090
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main () {
	int n,m,i;
	scanf("%d %d",&n,&m);
	m=m%(n*(n+1)/2);
	for(i=1;i<=n;i++)
		if(m>=i)
			m-=i;
	printf("%d\n",m);
	return 0;
}
