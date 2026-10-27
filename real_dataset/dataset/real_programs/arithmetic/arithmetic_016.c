// category: arithmetic  (real program 016)
// Codeforces submission 8661652, problem 486/A, GNU C++, 2014-11-11
// https://codeforces.com/contest/486/submission/8661652
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<math.h>

int main()
{
    long long   int n,i;
  scanf("%lld",&n);
 long long  int d,sum,odd,even,f;

      d=n/2;
      even=d*(d+1);
      f=n-d;
      odd=f*f;
      sum=even-odd;
    printf("%lld\n",sum);
    return 0;
}
