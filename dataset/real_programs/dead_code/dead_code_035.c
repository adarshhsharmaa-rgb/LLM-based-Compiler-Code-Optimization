// category: dead_code  (real program 035)
// Codeforces submission 1943840, problem 62/A, GNU C++, 2012-07-27
// https://codeforces.com/contest/62/submission/1943840
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,d,n,m=0,m1=0;
    scanf("%d%d%d%d",&a,&b,&c,&d);
    if((a*2+3>d&&d+1>=a)||(b*2+3>c&&c+1>=b))printf("YES");
    else printf("NO");
    return 0;
}
