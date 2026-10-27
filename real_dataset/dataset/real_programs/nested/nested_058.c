// category: nested  (real program 058)
// Codeforces submission 18777780, problem 669/A, GNU C++, 2016-06-29
// https://codeforces.com/contest/669/submission/18777780
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(){
    int n;
    scanf("%d", &n);
    printf("%d\n", (n*2/3 + (n%3 == 1)));
    return 0;
}
