// category: dead_code  (real program 019)
// Codeforces submission 41360585, problem 1017/C, C++14 (GCC 6-32), 2018-08-08
// https://codeforces.com/contest/1017/submission/41360585
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main()
{
    int n;
    scanf("%d", &n);
    int len = 0;
    for(len = 0; len * (len + 1) < n; len ++);

    int l1 = n % len;
    int l2 = n / len - l1;

    int x = n+1;
    int pos = 0;

    for(int i=0; i<l1; i++)
    {
        x -= (len+1);
        int now = x;
        for(int j=0; j<len+1; j++)
        {
            printf("%d ", now);
            now ++;
        }
    }


    for(int i=0; i<l2; i++)
    {
        x -= (len);
        int now = x;
        for(int j=0; j<len; j++)
        {
            printf("%d ", now);
            now ++;
        }
    }



    return 0;
}
