// category: mixed  (real program 004)
// Codeforces submission 20678562, problem 577/A, GNU C11, 2016-09-17
// https://codeforces.com/contest/577/submission/20678562
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
long long int count,i,n,x;count=0;
scanf("%lld%lld",&n,&x);
for(i=1;i<=n;i++)
if((x%i==0)&&(x<=(i*n)))
count++;
printf("%lld",count);
return 0;
}
