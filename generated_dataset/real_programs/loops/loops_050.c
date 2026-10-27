// category: loops  (real program 050)
// Codeforces submission 1813601, problem 171/G, GNU C++, 2012-06-22
// https://codeforces.com/contest/171/submission/1813601
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int a,b,c,i=1,n;
    scanf("%d %d %d",&a,&b,&n);
    while(i<n)
    {
        c=b;
        b=a+b;
        a=c;
        i++;
    }
    printf("%d",b);
}
