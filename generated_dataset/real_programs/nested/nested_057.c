// category: nested  (real program 057)
// Codeforces submission 7558597, problem 387/A, GNU C++, 2014-08-23
// https://codeforces.com/contest/387/submission/7558597
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){int a, b, c, d;scanf("%d:%d%d:%d", &a, &b, &c, &d);int e = (a * 60 + b - c * 60 - d + 2880) % 1440;printf("%02d:%02d\n", e / 60, e % 60);return 0;}
