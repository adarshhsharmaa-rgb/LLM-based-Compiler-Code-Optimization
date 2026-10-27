// category: nested  (real program 047)
// Codeforces submission 18295926, problem 486/A, GNU C, 2016-06-08
// https://codeforces.com/contest/486/submission/18295926
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    unsigned long long int n;

    scanf("%I64d",&n);

    printf("\n%I64d",n/2-(n%2)*n);

    return 0;

}
