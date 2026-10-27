// category: repeated_expr  (real program 021)
// Codeforces submission 19005309, problem 690/A2, GNU C++11, 2016-07-10
// https://codeforces.com/contest/690/submission/19005309
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <stdio.h>
using namespace std;

int N;

int main()
{
    int i;
    int num;
    int ans;

    scanf("%d",&N);

    num=1;

    while(num<=N)
    {
        if ( (N-num)%2==0 )
        ans=(N-num)/2;

        num*=2;
    }

    printf("%d\n",ans);

    return 0;
}
