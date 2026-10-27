// category: dead_code  (real program 008)
// Codeforces submission 16570801, problem 651/A, GNU C, 2016-03-07
// https://codeforces.com/contest/651/submission/16570801
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
    int n, i, j, count = 0,check = 0, a1, a2;
    scanf("%d %d", &a1, &a2);
    while (a1 > 0 && a2 > 0 && a1*a2 > 1) {
        if(a1 < a2) {
            a1++;
            a2-=2;
            count++;
        }
        else {
            a2++;
            a1-= 2;
            count++;
        }
    }
    printf("%d", count);
    return 0;
}
