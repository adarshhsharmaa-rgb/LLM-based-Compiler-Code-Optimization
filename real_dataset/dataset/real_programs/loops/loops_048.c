// category: loops  (real program 048)
// Codeforces submission 21966227, problem 492/A, GNU C11, 2016-11-01
// https://codeforces.com/contest/492/submission/21966227
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    int i=1,n;

    scanf("%d",&n);

    while(n>=0)

    {

        n-=((i)*(i+1))/2;

        i++;

    }

    printf("%d",i-2);

}
