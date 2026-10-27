// category: conditionals  (real program 031)
// Codeforces submission 20988588, problem 493/D, C++14 (GCC 6-32), 2016-09-29
// https://codeforces.com/contest/493/submission/20988588
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

typedef long long ll;
typedef unsigned long long ull;
typedef unsigned int uint;


int main()
{
    //freopen("input.txt", "r", stdin);
    //freopen(".out", "w+", stdout);
    //ios_base::sync_with_stdio( false );

    int n;
    scanf("%d", &n );

    if ( n%2==0 )
    {
        printf("white\n");
        printf("1 2\n");
    }
    else
        printf("black\n");

    return 0;
}
