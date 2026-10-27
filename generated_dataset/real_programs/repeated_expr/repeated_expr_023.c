// category: repeated_expr  (real program 023)
// Codeforces submission 33348230, problem 899/D, GNU C++, 2017-12-17
// https://codeforces.com/contest/899/submission/33348230
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
int main()
{
    long long n,b,i,t,ans=0;
    scanf("%I64d",&n);
    if(n<5)
    {
        printf("%I64d\n",(n*n-n)/2);
        return 0;
    }
    else if(n<50) b=5;
    else if(n<500) b=50;
    else if(n<5000) b=500;
    else if(n<50000) b=5000;
    else if(n<500000) b=50000;
    else if(n<5000000) b=500000;
    else if(n<50000000) b=5000000;
    else if(n<500000000) b=50000000;
    else b=500000000;
    for(i=b+b; i<b*20; i+=(b+b))
    {
        if(n>=i-2) ans+=(i-2)/2;
        else if(n>=i/2) ans+=(n-(i-2)/2);
    }
    printf("%I64d\n",ans);
    return 0;
}
