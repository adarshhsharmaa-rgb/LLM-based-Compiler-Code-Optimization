// category: conditionals  (real program 035)
// Codeforces submission 3429219, problem 171/D, GNU C++, 2013-04-01
// https://codeforces.com/contest/171/submission/3429219
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main(void){
int n;
scanf("%d",&n);
if(n!=5)printf("%d",(n%3)+1);
else printf("%d",1);
return 0;
}
