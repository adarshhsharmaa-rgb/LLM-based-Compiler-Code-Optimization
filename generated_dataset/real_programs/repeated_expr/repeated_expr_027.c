// category: repeated_expr  (real program 027)
// Codeforces submission 42164419, problem 1028/B, C++14 (GCC 6-32), 2018-08-27
// https://codeforces.com/contest/1028/submission/42164419
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
#define F first
#define S second

typedef long long ll;
using namespace std;

int main()
{
   // ios::sync_with_stdio(0); cin.tie(0); cout.tie(0);
    scanf("%*d%*d");
    for (int i = 0; i < 260; ++i)
        printf("%d", 4 + i % 2);
    printf("\n");
    for (int i = 1; i < 260; ++i)
        printf("%d", 4 + i % 2);
    printf("5\n");
    return 0;
}
