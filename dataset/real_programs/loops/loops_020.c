// category: loops  (real program 020)
// Codeforces submission 21305674, problem 327/B, C++14 (GCC 6-32), 2016-10-08
// https://codeforces.com/contest/327/submission/21305674
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

main()

{

    long long int n,i,j;

    scanf("%I64d",&n);

    for (i=n+1;i<=n*2;i++)

    printf("%d ",i);

    printf("\n");

    return 0;

}
