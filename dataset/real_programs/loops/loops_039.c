// category: loops  (real program 039)
// Codeforces submission 33692729, problem 909/B, GNU C, 2017-12-27
// https://codeforces.com/contest/909/submission/33692729
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>

int n, s;

int main()
{
    scanf("%d", &n);
    s = 0;
    while (n > 0)
    {
        s += n;
        n -= 2;
    }
    printf("%d", s);
    return 0;
}
