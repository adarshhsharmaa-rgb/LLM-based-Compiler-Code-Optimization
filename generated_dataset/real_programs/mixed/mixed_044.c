// category: mixed  (real program 044)
// Codeforces submission 22076842, problem 652/A, GNU C++, 2016-11-06
// https://codeforces.com/contest/652/submission/22076842
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main(void) {

    int h1, h2;

    int a, b;

    int day = 0;



    scanf(" %d %d", &h1, &h2);

    scanf(" %d %d", &a, &b);



    h1 += 8 * a;



    if (b >= a && h1 < h2) {

        day = -1;

    } else {

        while(h1 < h2) {

            day++;

            h1 += 12 * (a - b);

        }

    }

    printf("%d\n", day);

    return 0;

}
