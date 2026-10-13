// category: repeated_expr  (real program 052)
// Codeforces submission 36297190, problem 934/B, GNU C++, 2018-03-15
// https://codeforces.com/contest/934/submission/36297190
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include<string.h>
#include <algorithm>
#include<iostream>
#include<cstdlib>
#include<cstring>
#include<cstdio>
#include<queue>
using namespace std;
#define INF 0x3f3f3f3f

//int circle[10] = {1,0,0,0,1,0,1,0,2,1,};

int main()
{
    int n, m;
    scanf("%d", &n);
    if (n > 36) printf("-1");
    else
    {
        if (n % 2 == 0)
        {
            for (int i = 1; i <= n/2; i++)
            {
                printf("8");
            }
        }
        else
        {
            printf("6");
            n--;
            for (int i = 1; i <= n/2; i++)
            {
                printf("8");
            }
        }
    }
    return 0;
}
