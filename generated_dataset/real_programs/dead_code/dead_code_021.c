// category: dead_code  (real program 021)
// Codeforces submission 20361592, problem 678/A, GNU C++, 2016-09-03
// https://codeforces.com/contest/678/submission/20361592
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main()

{

    long long i, j, k, n, m, t, p, cas=1;

    scanf("%I64d %I64d", &n, &m);

    p=n%m;

    t=m-p;

    printf("%I64d\n", n+t);

    return 0;

}
