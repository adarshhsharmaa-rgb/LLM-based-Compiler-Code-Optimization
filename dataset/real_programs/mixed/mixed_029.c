// category: mixed  (real program 029)
// Codeforces submission 23446905, problem 750/A, C++14 (GCC 6-32), 2016-12-30
// https://codeforces.com/contest/750/submission/23446905
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
using namespace std;
int main()
{
    int n,i,k,t=240;
    scanf("%d%d",&n,&k);
    t-=k;
    i=0;
    while (t>0&&i<n)
    {
        ++i;
        t-=i*5;
    }
    if (t<0)
        --i;
    printf("%d\n",i);
    return 0;
}
