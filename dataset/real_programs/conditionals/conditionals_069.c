// category: conditionals  (real program 069)
// Codeforces submission 36457761, problem 950/A, GNU C11, 2018-03-21
// https://codeforces.com/contest/950/submission/36457761
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
    int l,r,a; int counter=0;
    scanf("%d %d %d",&l,&r,&a);
    if (r>l)
    {
        int temp=l;
        l=r;
        r=temp;
    }
    counter=counter+r;

    l=l-r;
    r=0;
    if(a>l)
    {
        counter=counter +l;
        a=a-l;
        l=0;
        counter=counter+a/2;
    }
    else
    {
        counter=counter+a;
    }
    counter=counter*2;
    printf("%d",counter);
}
