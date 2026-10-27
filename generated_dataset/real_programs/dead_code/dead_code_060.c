// category: dead_code  (real program 060)
// Codeforces submission 10675863, problem 534/A, GNU C, 2015-04-12
// https://codeforces.com/contest/534/submission/10675863
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{int a,b,c,d=1,e=2,f=3,g=4,i,j,k,count1=1,count2=2;
 scanf("%d",&a);
 if(a==2)
 {
              b=1;
              printf("%d\n",b);
              printf("%d",d);
 }
 else if(a==3)
 {
              b=2;

              printf("%d\n",b);
              printf("%d %d",d,f);

 }
 else if(a==4)
 {
              b=a;

              printf("%d\n",b);
              printf("%d %d %d %d",e,g,d,f);
 }
 else if(a!=2 && a!=3 && a!=4)
 {            b=a;
              printf("%d\n",b);
              for(i=1;i<=a;i=i+2)
              {    printf("%d ",i);


              }
              for(i=2;i<=a;i=i+2)
              {
                           printf("%d ",i);
              }


 }

return 0;
 }
