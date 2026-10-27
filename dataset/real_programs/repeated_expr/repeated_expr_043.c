// category: repeated_expr  (real program 043)
// Codeforces submission 60005085, problem 1214/B, GNU C11, 2019-09-04
// https://codeforces.com/contest/1214/submission/60005085
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
    int b,g,m,i,j,c=0;
    scanf("%d%d%d",&b,&g,&m);
    if(b<=m&&g<=m)
    {
        c=(b+g)-m+1;
        if(c<0)
        {
            printf("0\n");
        }
        else
        {
            printf("%d",c);
        }
    }
    else if(b>m&&g<=m){
        b=m;
        c=(b+g)-m+1;
        if(c<0)
        {
            printf("0\n");
        }
        else
        {
            printf("%d",c);
        }
    }
    else if(b<=m&&g>m){
        g=m;
        c=(b+g)-m+1;
        if(c<0)
        {
            printf("0\n");
        }
        else
        {
            printf("%d",c);
        }
    }
    else if(b>m&&g>m){
        b=m;
        g=m;
        c=(b+g)-m+1;
        if(c<0)
        {
            printf("0\n");
        }
        else
        {
            printf("%d",c);
        }
    }
}
