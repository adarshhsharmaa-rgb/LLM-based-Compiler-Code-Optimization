// category: repeated_expr  (real program 024)
// Codeforces submission 5856415, problem 195/A, GNU C++, 2014-01-31
// https://codeforces.com/contest/195/submission/5856415
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{int a,b,c,t;
scanf("%d%d%d",&a,&b,&c);
t=a*c/b-c;
if(a*c%b!=0)
t++;
printf("%d\n",t);
return 0;
}
