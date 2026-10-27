// category: loops  (real program 052)
// Codeforces submission 3704911, problem 306/A, GNU C++, 2013-05-12
// https://codeforces.com/contest/306/submission/3704911
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main() {
	int i,n,m;
	scanf("%d%d",&n,&m);
	int d = n/m, r = n%m;
	for(i=0;i<r;++i) printf("%d ",d+1);
	for(;i<m;++i) printf("%d ",d);
	return 0;
}
