// category: loops  (real program 029)
// Codeforces submission 36176041, problem 935/A, C++14 (GCC 6-32), 2018-03-10
// https://codeforces.com/contest/935/submission/36176041
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
  int n;
  scanf("%d", &n);
  int ans = 0;
  for (int i = 1; i <= n; ++i) {
    ans += (!(n % i));
  }
  printf("%d\n", ans - 1);
  return 0;
}
