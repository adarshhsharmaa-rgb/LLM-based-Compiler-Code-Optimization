// category: repeated_expr  (real program 053)
// Codeforces submission 21519640, problem 610/A, GNU C++11, 2016-10-17
// https://codeforces.com/contest/610/submission/21519640
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;



int main() {

    int n;

    scanf("%d", &n);

    if (n % 2 == 1) {

        puts("0");

        return 0;

    }

    if (n / 2 % 2 == 1)

        printf("%d\n", n / 2 / 2);

    else printf("%d\n", n / 2 / 2 - 1);

    return 0;

}
