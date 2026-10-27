// category: repeated_expr  (real program 044)
// Codeforces submission 43851049, problem 1059/C, GNU C++11, 2018-10-05
// https://codeforces.com/contest/1059/submission/43851049
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <stdio.h>

using namespace std;

int n;

int main() {
    scanf("%d", &n);
    int p = 1;

    while (n > 3) {
        for ( int i = 1; i <= (n/2 + n%2); i++ )
            printf("%d ", p);

        n = n - (n/2 + n%2);
        p = p * 2;
    }
    if ( n == 3 ) {
        printf("%d %d %d\n", p, p, p+p+p);
    } else if ( n == 2 ) {
        printf("%d %d\n", p, p + p);
    } else {
        printf("%d\n", p);
    }
        
    return 0;
}
