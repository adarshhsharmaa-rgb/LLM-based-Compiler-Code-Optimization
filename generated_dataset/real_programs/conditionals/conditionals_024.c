// category: conditionals  (real program 024)
// Codeforces submission 4327321, problem 39/D, GNU C++, 2013-08-23
// https://codeforces.com/contest/39/submission/4327321
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,d,e,f;
    scanf("%d%d%d%d%d%d",&a,&b,&c,&d,&e,&f);
    if((a==d)||(b==e)||(c==f))
        printf("YES\n");
    else
        printf("NO\n");
}
