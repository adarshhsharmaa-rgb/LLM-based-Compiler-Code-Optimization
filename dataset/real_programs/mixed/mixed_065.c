// category: mixed  (real program 065)
// Codeforces submission 21840762, problem 620/B, GNU C++11, 2016-10-28
// https://codeforces.com/contest/620/submission/21840762
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>

#include<cstdio>

#include<algorithm>



using namespace std;



int main()

{

    long a,b,sum=0,i,j;

    scanf("%ld%ld",&a,&b);



    for(i=a;i<=b;i++)

    {

        j=i;

        while(j>0)

        {

            a=j%10;

            j/=10;



            if(a==0)

                sum+=6;

            else if(a==1)

                sum+=2;

            else if(a==2)

                sum+=5;

            else if(a==3)

                sum+=5;

            else if(a==4)

                sum+=4;

            else if(a==5)

                sum+=5;

            else if(a==6)

                sum+=6;

            else if(a==7)

                sum+=3;

            else if(a==8)

                sum+=7;

            else if(a==9)

                sum+=6;

        }

    }



    printf("%ld",sum);

}
