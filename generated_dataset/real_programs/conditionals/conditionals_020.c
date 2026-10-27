// category: conditionals  (real program 020)
// Codeforces submission 20093086, problem 459/A, GNU C11, 2016-08-23
// https://codeforces.com/contest/459/submission/20093086
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    int a,b,c,d,m,n,x,y;

    scanf("%d%d%d%d",&a,&b,&c,&d);



    x=a-c;

    if(x<0)

        x=-x;

    y=b-d;

    if(y<0)

        y=-y;



    if(a!=c && b!=d)

    {

        if(x==y)

            printf("%d %d %d %d",c,b,a,d);

        else

            printf("-1");



    }



     if(a==c)

    {

        printf("%d %d %d %d",a+y,b,c+y,d);

    }



    else if(b==d)

    {

        printf("%d %d %d %d",a,x+b,c,x+d);

    }



    return 0;

}
