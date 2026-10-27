// category: nested  (real program 008)
// Codeforces submission 17721721, problem 670/A, GNU C++, 2016-05-05
// https://codeforces.com/contest/670/submission/17721721
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main ()
{
  int n;
  scanf ("%d", &n);
  printf ("%d %d\n", (n + 1) / 7 + n / 7, (n + 6) / 7 + (n + 5) / 7);
  return 0;
}
