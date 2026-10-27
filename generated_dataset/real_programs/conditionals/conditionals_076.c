// category: conditionals  (real program 076)
// Codeforces submission 20950411, problem 678/A, GNU C, 2016-09-27
// https://codeforces.com/contest/678/submission/20950411
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    int a,b,rem,ans;

    scanf("%d%d",&a,&b);

    if(a>=b)

    {

        rem=a%b;

        ans=a+(b-rem);

        printf("%d",ans);

    }

    else

        printf("%d",b);

    return 0;

}
