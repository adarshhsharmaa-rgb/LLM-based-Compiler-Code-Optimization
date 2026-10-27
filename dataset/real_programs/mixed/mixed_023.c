// category: mixed  (real program 023)
// Codeforces submission 11364305, problem 46/A, GNU C++, 2015-05-31
// https://codeforces.com/contest/46/submission/11364305
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
int n;
scanf("%d",&n);
int st = 1,i;
for(i=1;i<n;i++)
{
st = (st+i)%n;
if(st==0)st = n;
printf("%d ",st);
}
return 0;
}
