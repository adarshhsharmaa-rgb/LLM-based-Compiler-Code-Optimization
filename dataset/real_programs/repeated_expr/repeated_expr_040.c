// category: repeated_expr  (real program 040)
// Codeforces submission 31405699, problem 876/A, C++14 (GCC 6-32), 2017-10-16
// https://codeforces.com/contest/876/submission/31405699
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main()
{
    int n,a,b,c,ans=0;
    scanf("%d %d %d %d",&n,&a,&b,&c);
    if(a<=b)
    {
        if(c<=a)
        {
            if(n==1) ans=0;
            else if(n>=2) ans = a+((n-2)*c);
        }
        else ans = a*(n-1);
    }
    else
    {
        if(c<=b)
        {
            if(n==1) ans=0;
            else if(n>=2) ans = b+((n-2)*c);
        }
        else ans = b*(n-1);
    }
    printf("%d",ans);
    return 0;
}
