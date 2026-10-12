// category: dead_code  (real program 028)
// Codeforces submission 30154286, problem 854/B, C++14 (GCC 6-32), 2017-09-06
// https://codeforces.com/contest/854/submission/30154286
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
#include <algorithm>
#include <stack>
#include <map>
#include <set>
#include <queue>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
using namespace std;
const int N=1005;
long long n, k;
int main()
{
        scanf("%lld%lld", &n, &k);
        if(n==k || k==0) printf("0 ");
        else printf("1 ");
        if(k==0 || k==n) printf("0");
        else
        {
                if(3*k>=n) printf("%lld", n-k);
                else printf("%lld", 2*k);
        }
        return 0;
}
