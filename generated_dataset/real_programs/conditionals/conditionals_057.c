// category: conditionals  (real program 057)
// Codeforces submission 14191161, problem 125/A, GNU C++, 2015-11-11
// https://codeforces.com/contest/125/submission/14191161
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
int n;
scanf("%d",&n);
int m = n/3;
if(n%3==2)m++;
printf("%d %d\n",m/12,m%12);
return 0;
}
