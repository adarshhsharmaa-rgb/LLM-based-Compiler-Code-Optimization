// category: nested  (real program 053)
// Codeforces submission 1787535, problem 195/A, GNU C++, 2012-06-12
// https://codeforces.com/contest/195/submission/1787535
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<cstdlib>

int n,m,k;

int main(){
	scanf("%d%d%d",&n,&m,&k);
	printf("%d\n",((n*k+m-1)/m)-k);
	return 0;
}
