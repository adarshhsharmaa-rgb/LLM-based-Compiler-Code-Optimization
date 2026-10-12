// category: dead_code  (real program 045)
// Codeforces submission 5326734, problem 369/B, GNU C++, 2013-12-02
// https://codeforces.com/contest/369/submission/5326734
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

using namespace std;

int main () {
  int n,k,l,r,sall,sk;

  scanf("%d %d %d %d %d %d", &n, &k, &l, &r, &sall, &sk);

  sall -= sk;
  n -= k;
  while (k>0) {
    printf("%d ", sk/k);
    sk -= sk/k;
    k--;
  }

  while (n>0) {
    printf("%d ", sall/n);
    sall -= sall/n;
    n--;
  }


  return  0;
}
