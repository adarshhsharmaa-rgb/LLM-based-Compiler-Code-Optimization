// category: loops  (real program 017)
// Codeforces submission 22236079, problem 734/B, GNU C++, 2016-11-15
// https://codeforces.com/contest/734/submission/22236079
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
#include <stdio.h>

using namespace std;
int main()
{
    int a, sum  = 0;
    int k2 , k3, k5, k6;
    scanf("%d %d %d %d", &k2 ,&k3, &k5, &k6);
    while(k2 > 0  && k5 > 0 && k6 > 0 )
    {
        k2--;
        //k3--;
        k5--;
        k6--;
        sum += 256;
    }
    while(k2 > 0 && k3 > 0)
    {
        k2--;
        k3--;
        sum += 32;
    }
    printf("%d\n", sum);
    return 0;

}
