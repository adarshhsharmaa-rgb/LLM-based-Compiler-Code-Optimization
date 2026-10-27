// category: conditionals  (real program 060)
// Codeforces submission 28851182, problem 832/A, GNU C, 2017-07-24
// https://codeforces.com/contest/832/submission/28851182
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
    long long int n,k,div;
    scanf("%I64d %I64d",&n,&k);
    div=n/k;
    if(div%2!=0)
        printf("YES");
    else
        printf("NO");
    return 0;
}
