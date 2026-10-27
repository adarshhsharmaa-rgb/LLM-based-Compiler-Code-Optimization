// category: loops  (real program 034)
// Codeforces submission 12153461, problem 333/A, GNU C++, 2015-07-21
// https://codeforces.com/contest/333/submission/12153461
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
long long n,i;
int main() {
  scanf("%I64d",&n);
  for (i=1; n%i==0; i*=3);
  printf("%I64d\n",(n+i-1)/i);
  return 0;
}
