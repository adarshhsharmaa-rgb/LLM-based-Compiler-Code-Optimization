// category: mixed  (real program 058)
// Codeforces submission 37965644, problem 1212/A, GNU C, 2018-05-06
// https://codeforces.com/contest/1212/submission/37965644
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long long int a,b,i;
    scanf("%I64d %I64d",&a,&b);
    for(i=0;i<b;i++)
    {
        if(a%10==0)
        a=a/10;
        else
        a=a-1;
    }
    printf("%I64d",a);
    return 0;
}
