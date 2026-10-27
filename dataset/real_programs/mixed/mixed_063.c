// category: mixed  (real program 063)
// Codeforces submission 325965, problem 66/D, MS C++, 2011-03-07
// https://codeforces.com/contest/66/submission/325965
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
using namespace std;
typedef __int64 lint;
int main ()
{
    int n,i;
    scanf("%d",&n);
    if(n==2)
    {
        printf("-1\n");
        return 0;
    }
    printf("6\n10\n15\n");
    lint ans=15;
    for(i=3;i<n;i++)
    {
        ans*=2;
        printf("%I64d\n",ans);
    }
    return 0;
}
