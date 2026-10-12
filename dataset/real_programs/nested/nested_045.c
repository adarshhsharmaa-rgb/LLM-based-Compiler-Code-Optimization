// category: nested  (real program 045)
// Codeforces submission 8214083, problem 460/A, GNU C++, 2014-10-13
// https://codeforces.com/contest/460/submission/8214083
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
main()
{
   int n=0,m=0;
   scanf("%d %d",&n,&m);
   n+=(n-1)/(m-1);
   printf("%d",n);
}
