// category: nested  (real program 050)
// Codeforces submission 19878448, problem 622/B, GNU C++, 2016-08-15
// https://codeforces.com/contest/622/submission/19878448
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main(void) {

    int h, m;

    int a;

    int t;



    scanf(" %d:%d", &h, &m);

    scanf(" %d", &a);

    t = 60 * h + m + a;

    m = t % 60;

    t /= 60;

    h = t % 24;

    printf("%02d:%02d\n", h, m);

    return 0;

}
