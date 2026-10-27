// category: loops  (real program 030)
// Codeforces submission 3377807, problem 285/A, GNU C++, 2013-03-22
// https://codeforces.com/contest/285/submission/3377807
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
    int n,m;
      scanf("%d %d",&n,&m);
    for(int i=m+1;i>0;i--)printf("%d ",i);
     for(int i=m+2;i<=n;i++)printf("%d ",i);  
         
}
