// category: mixed  (real program 036)
// Codeforces submission 12671815, problem 58/B, GNU C++, 2015-08-23
// https://codeforces.com/contest/58/submission/12671815
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
int n;
scanf("%d",&n);
int m;
for(m=n;m>=1;m--)
{
if(n%m==0){
printf("%d ",m);
n=m;
}
}
return 0;
}
