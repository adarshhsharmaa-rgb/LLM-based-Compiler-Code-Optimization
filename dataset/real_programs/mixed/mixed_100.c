// category: mixed  (real program 100)
// Codeforces submission 22048067, problem 579/A, C++14 (GCC 6-32), 2016-11-05
// https://codeforces.com/contest/579/submission/22048067
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    int n,r,co=0;
    scanf("%d",&n);
    while(n>0)
    {
        r=n%2;
        if(r==1)
            co++;
        n/=2;
    }
    printf("%d\n",co);
}
