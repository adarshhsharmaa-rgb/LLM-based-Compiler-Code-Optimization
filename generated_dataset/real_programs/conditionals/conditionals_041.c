// category: conditionals  (real program 041)
// Codeforces submission 31084600, problem 869/B, GNU C++11, 2017-10-06
// https://codeforces.com/contest/869/submission/31084600
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    long long i,j,m;
    int n,p;

    scanf("%I64d%I64d",&i,&j);
    m=j-i;
    i++;
    if(m>0 && m<10)
    {
        n=j%10;
        p=i%10;
        if(n>p)
        {
            if(p>=1 && n<5){
                if(p==1)
                {
                    if(n==2)
                        printf("2\n");
                    else if(n==3)
                        printf("6\n");
                    else if(n==4)
                        printf("4\n");
                }
                else if(p==2)
                {
                    if(n==3)
                        printf("6\n");
                    else if(n==4)
                        printf("4\n");
                }
                else if(p==3)
                {
                    if(n==4)
                        printf("2\n");

                }
            }
            else if(p>=6 && n<10){
                if(p==6)
                {
                    if(n==7)
                        printf("2\n");
                    else if(n==8)
                        printf("6\n");
                    else if(n==9)
                        printf("4\n");
                }
                else if(p==7)
                {
                    if(n==8)
                        printf("6\n");
                    else if(n==9)
                        printf("4\n");
                }
                else if(p==8)
                {
                    if(n==9)
                        printf("2\n");
                }
            }
            else printf("0\n");
        }
        else if(n==p) printf("%d\n",n);
        else printf("0\n");
    }
    else if(m==0) printf("1\n");
    else printf("0\n");

    return 0;
}
