// category: conditionals  (real program 061)
// Codeforces submission 15448731, problem 257/B, GNU C++, 2016-01-20
// https://codeforces.com/contest/257/submission/15448731
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){
    int n,m;
    scanf("%d%d", &n, &m);
    if(n>m) printf("%d %d\n",n-1,m);
	else printf("%d %d\n",m-1,n);
	return 0;
}
