// category: loops  (real program 060)
// Codeforces submission 31074448, problem 869/B, GNU C++11, 2017-10-06
// https://codeforces.com/contest/869/submission/31074448
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    long long int a, b;
    int c;

    scanf("%I64d %I64d", &a, &b);

    c = 1;
    for(int i=0; i<5 && b > a && b > 0; i++)
    {
        c *= (b%10);
        b--;
    }

    printf("%d\n", c%10);

    return 0;
}
