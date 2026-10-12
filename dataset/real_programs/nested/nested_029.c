// category: nested  (real program 029)
// Codeforces submission 17017302, problem 628/A, GNU C++, 2016-03-29
// https://codeforces.com/contest/628/submission/17017302
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main() {
int a, b, c;
scanf("%d %d %d", &a, &b, &c);
printf("%d %d\n", (2 * b + 1) * (a - 1), a * c);
return 0;
}
