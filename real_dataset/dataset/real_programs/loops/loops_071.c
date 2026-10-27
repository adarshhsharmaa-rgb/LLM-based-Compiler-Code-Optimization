// category: loops  (real program 071)
// Codeforces submission 35677577, problem 935/A, GNU C++, 2018-02-25
// https://codeforces.com/contest/935/submission/35677577
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main()
{
 int n, cnt = 0;
 scanf("%d", &n);
 for (int i = 1; i <= n / 2; i++) {
  cnt += ((n - i) % i == 0);
 }
 printf("%d\n", cnt);
}
