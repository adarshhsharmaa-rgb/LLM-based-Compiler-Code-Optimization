// category: nested  (real program 037)
// Codeforces submission 16357699, problem 630/H, GNU C++, 2016-02-26
// https://codeforces.com/contest/630/submission/16357699
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    long long n, nPr, nCr;
    scanf("%I64d", &n);
    nCr=n*(n-1)*(n-2)*(n-3)*(n-4);
    nPr=nCr/120;
    printf("%I64d\n", nPr*nCr);

    return 0;
}
