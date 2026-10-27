// category: mixed  (real program 071)
// Codeforces submission 21804363, problem 492/A, GNU C, 2016-10-26
// https://codeforces.com/contest/492/submission/21804363
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

main()

{

    int n,i=0,y=0,k=0;

    scanf("%d", &n);

    while (k<n)

    {

        i++;

        y+=i;

        k+=y;

    }

    if (k>n)

    {

        i--;

    }

    printf("%d", i);

}
