// category: repeated_expr  (real program 050)
// Codeforces submission 20834089, problem 690/A1, GNU C11, 2016-09-23
// https://codeforces.com/contest/690/submission/20834089
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
int n;
scanf("%d",&n);
if(n%2==0)
printf("%d",n/2);
else
printf("%d",n/2+1);
return 0;
}
