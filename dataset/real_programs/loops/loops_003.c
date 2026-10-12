// category: loops  (real program 003)
// Codeforces submission 14183043, problem 136/B, GNU C++, 2015-11-10
// https://codeforces.com/contest/136/submission/14183043
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int a,b,c,t=1;
int main()
{
    scanf("%d%d",&a,&c);
    for(;a||c;a/=3,c/=3,t*=3)
        b+=(c%3-a%3+3)%3*t;
    printf("%d",b);
}
