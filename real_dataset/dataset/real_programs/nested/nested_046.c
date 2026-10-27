// category: nested  (real program 046)
// Codeforces submission 33292196, problem 898/A, GNU C, 2017-12-16
// https://codeforces.com/contest/898/submission/33292196
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
# include <stdio.h>

int main()
{
    int n;
    scanf("%d", &n);
    n = ((n+5)/10)*10;
    printf("%d", n);
    return 0;
}
