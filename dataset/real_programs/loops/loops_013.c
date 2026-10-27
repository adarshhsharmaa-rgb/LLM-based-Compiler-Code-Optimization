// category: loops  (real program 013)
// Codeforces submission 3688252, problem 92/A, GNU C++, 2013-05-06
// https://codeforces.com/contest/92/submission/3688252
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
main()
{
    int n,m,i;
    scanf("%d%d",&n,&m);
    m%=(n*(n+1)/2);
    for(int i=1;i<=m;i++)
    m-=i;
    printf("%d\n",m);
}
