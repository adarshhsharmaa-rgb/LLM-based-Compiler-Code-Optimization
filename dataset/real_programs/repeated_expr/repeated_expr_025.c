// category: repeated_expr  (real program 025)
// Codeforces submission 2483041, problem 241/G, GNU C++0x, 2012-11-01
// https://codeforces.com/contest/241/submission/2483041
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
  int n = 500, m = 1000000, x, r;

  printf("%d\n", n);
  x = 0;
  r = m;
  x = m / 2;
  printf("%d %d\n", x, r);
  for (int i = 1; i < n - 1; ++i) {
    x += 2 * (n - i) + 1;
    r = n - i;
    printf("%d %d\n", x, r);
  }
  x = m;
  r = m;
  printf("%d %d\n", x, r);

  return 0;
}
