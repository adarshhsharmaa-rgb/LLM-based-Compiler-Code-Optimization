// category: mixed  (real program 042)
// Codeforces submission 41352375, problem 1017/C, GNU C++11, 2018-08-08
// https://codeforces.com/contest/1017/submission/41352375
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <utility>

using namespace std;

int main() {
  int n; scanf("%d", &n);

  int s = 1;
  for(int lx = 1;lx <= n;lx++) {
    if(s + (n+s-1)/s > lx + (n+lx-1)/lx)
      s = lx;
  }

  for(int lx = 1;lx <= n/s;lx++) {
    for(int ly = 1;ly <= s;ly++) {
      printf("%d ", n-lx*s + ly);
    }
  }
  for(int lx = 1;lx <= n%s;lx++) {
    printf("%d ", lx);
  }
  puts("");
  return 0;
}
