// category: loops  (real program 055)
// Codeforces submission 39618131, problem 996/A, GNU C, 2018-06-24
// https://codeforces.com/contest/996/submission/39618131
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
  int n,c=0;
  scanf("%d",&n);
  while(n>=100)
  {
    n=n-100;
    c++;
  }
  while(n>=20)
  {
    n=n-20;
    c++;
  }
  while(n>=10)
  {
    n=n-10;
    c++;
  }
  while(n>=5)
  {
    n=n-5;
    c++;
  }
  printf("%d\n",c+n);
}
