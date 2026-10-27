// category: nested  (real program 002)
// Codeforces submission 20396207, problem 486/A, GNU C11, 2016-09-05
// https://codeforces.com/contest/486/submission/20396207
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
long long n,y;
scanf("%lld",&n);
y=((n+(n%2))/2);
printf("%lld", ((n*n)-(2*n*y)+n-y));
return 0;
}
