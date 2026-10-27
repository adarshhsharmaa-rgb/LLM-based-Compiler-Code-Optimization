// category: mixed  (real program 050)
// Codeforces submission 35865272, problem 937/B, GNU C++, 2018-03-03
// https://codeforces.com/contest/937/submission/35865272
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <string>
using namespace std;

int main()
{
 int p,y,i,flag=0;
 scanf("%d%d",&p,&y);
 for(i=y;i>p;i--)
 {
  for(int j=2;j<=p&&j*j<=i;j++)
  {
   if(i%j==0)
   {
    flag=1;
    j=p;
   }
  }
  if(!flag)
  {
   printf("%d\n",i);
   return 0;
  }
  flag=0;
 }
 printf("-1\n");
 return 0;
}
