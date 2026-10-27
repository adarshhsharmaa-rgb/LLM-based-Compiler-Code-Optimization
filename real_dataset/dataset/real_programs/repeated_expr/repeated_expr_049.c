// category: repeated_expr  (real program 049)
// Codeforces submission 10683324, problem 534/B, GNU C++, 2015-04-12
// https://codeforces.com/contest/534/submission/10683324
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<stdio.h>

int main()
{
    int v1,v2,t,d,sum,temp_sum,diff,temp_diff,i,time,temp;

    scanf("%d%d",&v1,&v2);
    scanf("%d%d",&t,&d);

    if(v1>v2)
    {
        temp=v1;
        v1=v2;
        v2=temp;
    }

    if(v1<v2)
    {
        temp=v1;
        sum=temp;
        time=1;

        //printf("%d ",temp);


        while(temp<v2 && time<t-1)
        {
            temp=temp+d;
            //printf("%d ",temp);
            sum=sum+temp;
            time++;
        }

        diff=t-time-1;

        if(temp<=v2 && diff==0)
        {
            //printf("%d ",v2);
            sum=sum+v2;
        }
        else if(temp>=v2)
        {
            temp_diff=temp-v2;

            if(diff==0)
               {
                   //printf("%d ",v2);
                   sum=sum+v2;
               }
            else
               {
                   if(diff==1)
                   {
                       //printf("%d ",temp+d);
                       sum=sum+temp+d;
                       sum=sum-temp_diff;
                   }
                   else if(diff%2==0)
                   {
                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp+d;
                           //printf("%d ",temp);
                           sum=sum+temp;
                       }

                       temp=temp+d-temp_diff;


                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp-d;
                           //printf("%d ",temp);
                           sum=sum+temp;
                       }
                   }
                   else if(diff%2!=0)
                   {

                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp+d;
                           //printf("%d ",temp);
                           sum=sum+temp;
                       }

                       temp=temp+d-temp_diff;
                       sum=sum+temp;

                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp-d;
                           //printf("%d ",temp);
                           sum=sum+temp;
                       }

                   }
                   sum=sum+v2;
               }

        }
    }
    else if(v1==v2)
    {
          sum=0;



        if(t==3)
                   {
                       sum=v1+(v1+d)+v1;
                   }
        else if(t%2==0)
                   {
                       diff=t-2;
                       temp_sum=0;
                       temp=v1;

                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp+d;
                           //printf("%d ",temp);
                           temp_sum=temp_sum+temp;
                       }
                       sum=sum+(2*temp_sum);
                       sum=sum+(2*v1);
                   }
        else if(t%2!=0)
                   {
                       diff=t-2;
                       temp_sum=0;
                       temp=v1;

                       for(i=1;i<=(diff/2);i++)
                       {
                           temp=temp+d;
                           //printf("%d ",temp);
                           temp_sum=temp_sum+temp;
                       }
                       sum=sum+(temp+d);
                       //printf("%d ",temp+d);
                       sum=sum+(2*temp_sum);
                       sum=sum+(2*v1);

                   }
     }

    printf("%d",sum);
    return 0;
}
