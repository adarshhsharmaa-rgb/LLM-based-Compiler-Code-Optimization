// category: nested  (real program 017)
// Codeforces submission 39622856, problem 996/A, GNU C11, 2018-06-24
// https://codeforces.com/contest/996/submission/39622856
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long int n,z1=0,k1=0,k2=0,k3=0,k4=0,k5=0,sum=0;
    scanf("%ld",&n);
    z1=n%100;
            k1=n/100;
            n=0;
     n=z1;
     z1=n%20;
            k2=(n/20);
     n=0;
         n=z1;
         z1=n%10;
                k3=(n/10);
    n=0;
         n=z1;
         z1=n%5;
            k4=(n/5);
                n=0;
            n=z1;
         z1=n%1;
             k5=(n/1);
             sum=k1+k2+k3+k4+k5;
             printf("%ld",sum);
return 0;}
