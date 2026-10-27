// category: repeated_expr  (real program 009)
// Codeforces submission 23448537, problem 750/A, GNU C++11, 2016-12-30
// https://codeforces.com/contest/750/submission/23448537
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>

using namespace std;

int main()
{
    int n, k, tol = 0, num = 0;

    scanf("%d%d", &n, &k);
    while(tol + (num + 1) * 5 + k <= 240 && num + 1 <= n){
        num++;
        tol += num * 5;
    }
    printf("%d\n", num);
    return 0;
}
