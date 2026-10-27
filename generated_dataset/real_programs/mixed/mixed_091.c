// category: mixed  (real program 091)
// Codeforces submission 448147, problem 84/A, GNU C++, 2011-05-13
// https://codeforces.com/contest/84/submission/448147
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
main()
{
    int n,i,s=0;
    scanf("%i",&n);
    if(n%2==0)
    {
        for(i=0;i<n;i++)
        {
            s+=3;
        }
    }
    printf("%i",s/2);
    return 0;
}
