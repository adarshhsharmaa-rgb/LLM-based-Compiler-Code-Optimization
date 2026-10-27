// category: arithmetic  (real program 020)
// Codeforces submission 19846696, problem 622/B, GNU C++11, 2016-08-13
// https://codeforces.com/contest/622/submission/19846696
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main() {
  int a, b, c;
  scanf("%d:%d", &a, &b);
  scanf("%d", &c);
  int n = a * 60 + b;
  n += c;
  n %= 24 * 60;
  printf("%02d:%02d\n", n/60, n % 60);

  return 0;
}
