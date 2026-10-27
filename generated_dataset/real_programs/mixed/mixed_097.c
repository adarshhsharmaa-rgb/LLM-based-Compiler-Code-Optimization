// category: mixed  (real program 097)
// Codeforces submission 10681378, problem 534/B, GNU C11, 2015-04-12
// https://codeforces.com/contest/534/submission/10681378
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int v1, v2;
    int t, d;
    int sum = 0;
    int lv_l, lv_r, T;
    scanf("%d", &v1);
    scanf("%d", &v2);
    scanf("%d", &t);
    scanf("%d", &d);

    lv_l = v1;
    lv_r = v2;
    T = t - 1;
    while (T > 1)
    {
        if (lv_l <= lv_r)
        {
            sum += lv_l;
            lv_l += d;
        }
        else
        {
            sum += lv_r;
            lv_r += d;
        }
        T--;
    }

    sum += lv_l;
    sum += lv_r;

    printf("%d\n", sum);
    return 0;

}
