// category: conditionals  (real program 044)
// Codeforces submission 8253236, problem 478/A, GNU C++, 2014-10-16
// https://codeforces.com/contest/478/submission/8253236
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int a,b,c,d,e,s;
main()
{
    scanf("%d%d%d%d%d",&a,&b,&c,&d,&e);
    s=a+b+c+d+e;
    if(s%5||s==0)printf("-1");
    else printf("%d",s/5);
}
