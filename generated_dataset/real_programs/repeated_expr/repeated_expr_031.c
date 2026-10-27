// category: repeated_expr  (real program 031)
// Codeforces submission 7579524, problem 194/A, GNU C++, 2014-08-26
// https://codeforces.com/contest/194/submission/7579524
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
int n,k;

scanf("%d%d",&n,&k);


if(k<3*n)
printf("%d\n",(3*n-k));
else
printf("0\n");
return 0;
}
