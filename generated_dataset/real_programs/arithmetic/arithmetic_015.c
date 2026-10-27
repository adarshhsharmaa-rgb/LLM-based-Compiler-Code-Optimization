// category: arithmetic  (real program 015)
// Codeforces submission 12421629, problem 125/A, GNU C++, 2015-08-09
// https://codeforces.com/contest/125/submission/12421629
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int x;
int main()
{
    scanf("%d",&x);
    x += 1; int tmp = x / 3;
    printf("%d %d\n",tmp/12,tmp%12);
}
