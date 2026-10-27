// category: dead_code  (real program 026)
// Codeforces submission 28849664, problem 832/A, GNU C++, 2017-07-24
// https://codeforces.com/contest/832/submission/28849664
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
#include<cmath>
using namespace std;

int main()
{
    long long int n, k, sasha = 0, lina = 0;
    scanf("%I64d %I64d", &n, &k);

    long long int test = n / k;
    if(test % 2 == 0) printf("NO\n");
    else printf("YES\n");
}
