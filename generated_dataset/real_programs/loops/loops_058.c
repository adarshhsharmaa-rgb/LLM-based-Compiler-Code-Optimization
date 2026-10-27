// category: loops  (real program 058)
// Codeforces submission 2637645, problem 92/A, GNU C++, 2012-11-24
// https://codeforces.com/contest/92/submission/2637645
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
main(){
    int n,m,i;
    scanf("%d%d",&n,&m);
    m%=(n*(n+1)/2);
    for(i=1;i<=m;i++)m-=i;
    printf("%d\n",m);
}
