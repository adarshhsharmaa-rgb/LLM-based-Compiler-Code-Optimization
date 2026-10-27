// category: mixed  (real program 014)
// Codeforces submission 47426950, problem 1085/B, MS C++, 2018-12-23
// https://codeforces.com/contest/1085/submission/47426950
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h> 
int main () 
{
long long  n, x=-1, a, k, j; 
scanf ("%I64d%I64d", &n, &k);
for (j=1; j<k; j++)
{
if (n%j==0)
{
a=n/j*k+j;
if(((a/k)*(a%k)==n) && (a<x || x==-1))
x=a;
}
}
printf ("%I64d", x);
return 0;
}
