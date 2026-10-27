// category: arithmetic  (real program 047)
// Codeforces submission 39617931, problem 996/A, GNU C, 2018-06-24
// https://codeforces.com/contest/996/submission/39617931
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
    int a , count=0;

    scanf("%d",&a);
    count=count+a/100;
    a=a%100;

    count=count+a/20;
    a=a%20;
    count=count+a/10;
    a=a%10;
    count=count+a/5;
    a=a%5;

    count=count+a;
    printf("%d\n",count);

    return 0;

}
