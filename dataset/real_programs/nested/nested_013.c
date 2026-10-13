// category: nested  (real program 013)
// Codeforces submission 16358007, problem 630/F, GNU C++, 2016-02-26
// https://codeforces.com/contest/630/submission/16358007
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    long long five, six, seven, n;
    scanf("%I64d", &n);
    five=(n*(n-1)*(n-2)*(n-3)*(n-4))/120;
    six=(five*(n-5))/6;
    seven=(six*(n-6))/7;

    printf("%I64d\n", five+six+seven);

    return 0;
}
