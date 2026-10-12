// category: loops  (real program 051)
// Codeforces submission 9731314, problem 136/B, GNU C++, 2015-02-05
// https://codeforces.com/contest/136/submission/9731314
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
    int i,a,c,b=0;
    scanf("%d %d",&a,&c);
    for(i=1;a>0||c>0;i*=3,a/=3,c/=3)
    {
        b+=((3+(c%3)-(a%3))%3)*i;
    }
    printf("%d",b);
    return 0;
}
