// category: conditionals  (real program 018)
// Codeforces submission 30882980, problem 865/A, C++14 (GCC 6-32), 2017-09-30
// https://codeforces.com/contest/865/submission/30882980
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    int a;
    scanf("%d", &a);
    if (a == 1)
    {
        printf("1 1\n1\n");
        return 0;
    }
    printf("%d %d\n", 2*(a-1), 2);
    printf("1 2\n");
return 0;
}
