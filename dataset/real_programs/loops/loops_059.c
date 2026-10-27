// category: loops  (real program 059)
// Codeforces submission 23435421, problem 750/A, GNU C++, 2016-12-30
// https://codeforces.com/contest/750/submission/23435421
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

using namespace std;

int main()
{
    int n,k;
    scanf("%d%d",&n,&k);
    int i=0;
    while(5*i*(i+1)/2+k<=240 && i<=n)i++;
    printf("%d",i-1);
    return 0;
}
