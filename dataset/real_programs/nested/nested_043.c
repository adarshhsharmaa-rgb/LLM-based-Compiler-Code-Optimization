// category: nested  (real program 043)
// Codeforces submission 20910565, problem 678/A, GNU C, 2016-09-25
// https://codeforces.com/contest/678/submission/20910565
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
long long int n,k;
scanf("%lld %lld",&n,&k);
printf("%lld",k*((n/k+1)));
return 0;
}
