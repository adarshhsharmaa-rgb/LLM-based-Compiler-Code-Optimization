// category: arithmetic  (real program 023)
// Codeforces submission 20920779, problem 678/A, GNU C11, 2016-09-26
// https://codeforces.com/contest/678/submission/20920779
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main ()
{
int n,k,y,x;
scanf("%d %d",&n,&k);
x=n/k;
y=k*(x+1);
printf("%d",y);
return 0;
}
