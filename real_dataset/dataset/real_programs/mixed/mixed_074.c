// category: mixed  (real program 074)
// Codeforces submission 30141927, problem 854/B, C++14 (GCC 6-32), 2017-09-06
// https://codeforces.com/contest/854/submission/30141927
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<string.h>
#include<algorithm>
using namespace std;

int main()
{
    int n,k;
    scanf("%d%d",&n,&k);
    int x=n;
    while(x%3)
        ++x;
    int a=x/3;
    if(n==k)
        printf("0 0\n");
    else if(k==0)
        printf("0 0\n");
    else
    {
        if(k>=a)
            printf("1 %d\n",n-k);
        else
            printf("1 %d\n",2*k);
    }
    return 0;
}
