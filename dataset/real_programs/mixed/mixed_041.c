// category: mixed  (real program 041)
// Codeforces submission 340988, problem 68/A, GNU C++, 2011-03-18
// https://codeforces.com/contest/68/submission/340988
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

main()
{
  int s,p1,p2,p3,p4,a,b,p,i;
  
  scanf("%d%d%d%d%d%d",&p1,&p2,&p3,&p4,&a,&b);
  
  s=0;
  for (i=a;i<=b;i++)
  {
    p=(((i%p1)%p2)%p3)%p4;  
    if (p==i) s++;
  }
  
  printf("%d\n",s);
}
