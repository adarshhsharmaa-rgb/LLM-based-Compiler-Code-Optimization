// category: arithmetic  (real program 035)
// Codeforces submission 20920221, problem 678/A, GNU C, 2016-09-26
// https://codeforces.com/contest/678/submission/20920221
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main ()
{
long long n,k;
scanf("%lld%lld",&n,&k);
long long l=n/k;
printf("%lld",k*(l+1));
return 0;}
