// category: repeated_expr  (real program 018)
// Codeforces submission 37936478, problem 1212/A, GNU C++11, 2018-05-06
// https://codeforces.com/contest/1212/submission/37936478
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int n, k;



int main()
{
    scanf("%d%d", &n, &k);
    while(k>0)
    {
        if(n%10==0)
        {
            k--;
            n/=10;

        }
        else
        {
            if(n%10>k)
            {
                n-=k;
                k-=k;
            }
            else
            {
                k-=n%10;
                n-=n%10;
            }
        }

    }

    printf("%d\n", n);


    return 0;
}
