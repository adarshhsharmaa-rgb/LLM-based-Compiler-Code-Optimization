// category: arithmetic  (real program 024)
// Codeforces submission 33684553, problem 909/B, C++14 (GCC 6-32), 2017-12-27
// https://codeforces.com/contest/909/submission/33684553
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include "bits/stdc++.h"
using namespace std;

int n;

int main()
{
    scanf("%d", &n);
    n++;
    printf("%d", (n * n) / 4);
    return 0;
}
