// category: loops  (real program 038)
// Codeforces submission 21614418, problem 268/B, GNU C, 2016-10-20
// https://codeforces.com/contest/268/submission/21614418
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{int n,b,ans,sum=0;

scanf("%d",&n);

for(b=1;b<n;b++)

    sum=sum+((n-b)*b);

ans=sum+n;

printf("\n%d",ans);}
