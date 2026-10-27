// category: loops  (real program 045)
// Codeforces submission 4597543, problem 322/A, GNU C++, 2013-09-28
// https://codeforces.com/contest/322/submission/4597543
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int m,n;
int main(){
	scanf("%d%d",&n,&m);
	printf("%d\n",m+n-1);
	for (int i=1;i<=m;i++) printf("%d %d\n",1,i);
	for (int i=2;i<=n;i++) printf("%d %d\n",i,1);
}
