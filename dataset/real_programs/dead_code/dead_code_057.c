// category: dead_code  (real program 057)
// Codeforces submission 23432200, problem 750/A, GNU C, 2016-12-30
// https://codeforces.com/contest/750/submission/23432200
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
     int main(void)
     {
         int n,i,j,k,t=22,v=6,c=0,sum=0,w;
         scanf("%d %d",&n,&k);
         sum=240-k;
         for(i=1;i<=n;i++)
         {
             if(sum>=0)
             {
                 sum-=i*5;
                 if(sum>=0)
                 {
                    c++;
                 }
             }
         }
         printf("%d",c);
         return 0;
     }
