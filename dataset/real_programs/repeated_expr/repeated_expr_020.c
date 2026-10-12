// category: repeated_expr  (real program 020)
// Codeforces submission 28845115, problem 832/A, C++14 (GCC 6-32), 2017-07-24
// https://codeforces.com/contest/832/submission/28845115
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    long long int n,k,a;
    scanf("%lld %lld",&n,&k);
    a=n/k;
    if(a%2!=0)
    {
        printf("YES\n");
    }
    else if(a%2==0)
    {
        printf("NO\n");
    }
    else{
        printf("NO\n");
    }


    return 0;
}
