// category: conditionals  (real program 042)
// Codeforces submission 44312275, problem 1064/A, GNU C11, 2018-10-14
// https://codeforces.com/contest/1064/submission/44312275
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,sum=0;

    scanf("%d%d%d",&a,&b,&c);


    if(a>b&&a>c)
    {
        sum=b+c;
        if(sum<=a)
        {
          printf("%d\n",(a-sum+1));
        }
        else {
            printf("0\n");
        }
    }
   else if(b>a&&b>c)
    {
        sum=a+c;
        if(sum<=b)
        {
          printf("%d\n",(b-sum+1));
        }
        else {
            printf("0\n");
        }
    }
    else
    {
        sum=b+a;
        if(sum<=c)
        {
          printf("%d\n",(c-sum+1));
        }
        else {
            printf("0\n");
        }
    }


}
