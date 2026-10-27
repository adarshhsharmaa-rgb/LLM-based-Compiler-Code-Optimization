// category: conditionals  (real program 038)
// Codeforces submission 21546619, problem 669/A, C++14 (GCC 6-32), 2016-10-17
// https://codeforces.com/contest/669/submission/21546619
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    int n;
    scanf("%d",&n);
    int ans=0;
    ans=n/3;
    ans*=2;
    if(n%3!=0)
        ans++;
    printf("%d\n",ans);
}
