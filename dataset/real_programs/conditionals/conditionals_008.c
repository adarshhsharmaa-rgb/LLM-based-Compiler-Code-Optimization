// category: conditionals  (real program 008)
// Codeforces submission 39577437, problem 991/A, GNU C, 2018-06-23
// https://codeforces.com/contest/991/submission/39577437
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,n;
    scanf("%d%d%d%d",&a,&b,&c,&n);
    if(c>a||c>b||n<0||n>100)
    {
        printf("-1");
        exit(0);
    }
    int res=n-((a-c)+b);
    if(res>0)
    printf("%d",res);
    else
    {
        int d=-1;
        printf("%d",d);
    }
   
    return 0;
}
