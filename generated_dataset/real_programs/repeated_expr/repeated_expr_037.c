// category: repeated_expr  (real program 037)
// Codeforces submission 32266918, problem 886/A, GNU C, 2017-11-12
// https://codeforces.com/contest/886/submission/32266918
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,d,e,f;
    scanf("%d %d %d %d %d %d",&a,&b,&c,&d,&e,&f);
    if(a+b+c==d+e+f || a+b+d==c+e+f ||  a+b+e==c+d+f || a+b+f==c+d+e || b+c+d==a+e+f || b+c+e==a+d+f || b+c+f==a+d+e || b+d+e==a+c+f || b+d+f==a+c+e || b+e+f==a+c+d || c+d+e==a+b+f ||c+d+f==a+b+e )
     printf("YES\n");
    else
        printf("NO\n");
    return 0;
}
