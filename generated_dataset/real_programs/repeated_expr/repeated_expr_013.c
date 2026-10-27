// category: repeated_expr  (real program 013)
// Codeforces submission 36855124, problem 952/A, GNU C, 2018-04-01
// https://codeforces.com/contest/952/submission/36855124
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
int a;
scanf("%d",&a);
if(a>=10&&a<=999&&a%2!=0)
    printf("1");
if(a>=10&&a<=999&&a%2==0)
    printf("0");
return 0;
}
