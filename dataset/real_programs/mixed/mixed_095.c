// category: mixed  (real program 095)
// Codeforces submission 18455103, problem 678/C, GNU C, 2016-06-14
// https://codeforces.com/contest/678/submission/18455103
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

          long long n,a,b,p,q;

          long long i,j,t,l,c,d,e,sum;

          scanf("%I64d",&n);

          scanf("%I64d",&a);

          scanf("%I64d",&b);

          scanf("%I64d",&p);

          scanf("%I64d",&q);

          i=a;

          j=b;

          while(j!=0)

          {

                    t=j;

                    j=i%j;

                    i=t;

          }

          l=(a*b)/i;

          c=n/a;

          d=n/b;

          e=n/l;

          if(p>=q)

          sum=(c*p)+((d-e)*q);

          else

          sum=(d*q)+((c-e)*p);

          printf("%I64d",sum);

          return 0;

}
