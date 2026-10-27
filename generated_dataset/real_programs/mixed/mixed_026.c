// category: mixed  (real program 026)
// Codeforces submission 37001523, problem 935/A, GNU C, 2018-04-05
// https://codeforces.com/contest/935/submission/37001523
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int n, i, cnt=0;
    scanf("%d",&n);
    for(i=2;i<=n;i++)
    {
        if(n%i==0)
            cnt++;
    }
    printf("%d",cnt);
}
