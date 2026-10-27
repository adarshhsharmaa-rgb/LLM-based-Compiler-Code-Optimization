// category: mixed  (real program 049)
// Codeforces submission 55248049, problem 1173/B, C++17 (GCC 7-32), 2019-06-07
// https://codeforces.com/contest/1173/submission/55248049
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstring>
#include <vector>


int main() {
  int n;
  scanf("%d", &n);
  int m = 1;
  while (2 * m - 1 < n) ++ m;
  printf("%d\n", m);
  for (int x = 1, y = 1, i = 0; i < n; ++ i) {
    printf("%d %d\n", x, y);
    if (y < m) ++ y;
    else ++ x;
  }
}
