// category: conditionals  (real program 078)
// Codeforces submission 7125639, problem 448/A, GNU C++, 2014-07-17
// https://codeforces.com/contest/448/submission/7125639
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(void)
{
    int a,b,c,d,e,f,n;
    scanf("%d%d%d",&a,&b,&c);
    scanf("%d%d%d",&d,&e,&f);
    scanf("%d",&n);
    if((a+b+c+4)/5+(d+e+f+9)/10<=n) printf("YES");
    else printf("NO");
}
