// category: nested  (real program 020)
// Codeforces submission 18170370, problem 387/A, GNU C++, 2016-05-31
// https://codeforces.com/contest/387/submission/18170370
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
main()
{
    int a,b,c,d;
    scanf("%d:%d%d:%d",&a,&b,&c,&d);
    printf("%02d:%02d",(a-c-(d>b)+24)%24,(b-d+60)%60);
}
