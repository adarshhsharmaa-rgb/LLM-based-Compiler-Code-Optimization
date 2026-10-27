// category: arithmetic  (real program 022)
// Codeforces submission 33290701, problem 898/A, GNU C++, 2017-12-16
// https://codeforces.com/contest/898/submission/33290701
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    long long n;
    scanf("%I64d",&n);
    n=n+5;
    n-=(n%10);
    printf("%I64d\n",n);
    return 0;
}
