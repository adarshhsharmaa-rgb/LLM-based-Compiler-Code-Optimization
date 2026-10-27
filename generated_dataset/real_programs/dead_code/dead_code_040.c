// category: dead_code  (real program 040)
// Codeforces submission 42176927, problem 1028/B, GNU C++11, 2018-08-27
// https://codeforces.com/contest/1028/submission/42176927
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
using namespace std;
#include <cstdio>

const int maxn = 500;
int n, m;

int main() {
  scanf("%d %d", &n, &m);
  int d = 5;
  for (int i = 1; i <= maxn; ++i) {
    printf("%d", d);
    d = 9-d;
  }
  puts("5");
  d = 4;
  for (int i = 1; i <= maxn; ++i) {
    printf("%d", d);
    d = 9-d;
  }
  puts("5");
  return 0;
}
