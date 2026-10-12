// category: loops  (real program 037)
// Codeforces submission 44637965, problem 1031/A, C++17 (GCC 7-32), 2018-10-21
// https://codeforces.com/contest/1031/submission/44637965
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

long w,h,k;
long i,j,s,p;

int main()
{
    scanf("%d%d%d",&w,&h,&k);

    for ( i = 0 ; i < k ; i++ )
    {
        p=w+w+h+h-4;
        s=s+p;
        w=w-4;
        h=h-4;
    }

    printf("%d",s);

    return 0;
}
