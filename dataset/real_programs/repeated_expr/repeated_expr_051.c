// category: repeated_expr  (real program 051)
// Codeforces submission 14021716, problem 579/A, GNU C++11, 2015-11-02
// https://codeforces.com/contest/579/submission/14021716
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main ()
{
    int x,i,answer=0,temp;
    scanf("%d",&x);
    while(x!=0)
    {
       i=1;
      while(i<=x)
        i*=2;

      i/=2;
      answer+=x/i;
      temp=x/i;

      x-=i*temp;
    }
    printf("%d\n",answer);

    return 0;
}
