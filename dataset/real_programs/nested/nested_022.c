// category: nested  (real program 022)
// Codeforces submission 44628943, problem 1031/A, GNU C++11, 2018-10-21
// https://codeforces.com/contest/1031/submission/44628943
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
    int w,h,k;
    scanf("%d %d %d",&w,&h,&k);
    int ans = 2 * k * (w + h) - 8 * k * k + 4 * k;
    printf("%d\n",ans);
    return 0;
}
