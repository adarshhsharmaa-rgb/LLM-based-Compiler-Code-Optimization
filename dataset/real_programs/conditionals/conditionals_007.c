// category: conditionals  (real program 007)
// Codeforces submission 663124, problem 112/B, GNU C++, 2011-09-03
// https://codeforces.com/contest/112/submission/663124
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
    int n,x,y,n1,n2;
    scanf("%d%d%d",&n,&x,&y);
    n1=n/2;
    n2=n1+1;
    if((x==n1 || x==n2) && (y==n1 || y==n2)) printf("NO\n");
    else printf("YES\n");
	return 0;
}
