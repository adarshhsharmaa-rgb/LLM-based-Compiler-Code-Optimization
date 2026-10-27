// category: conditionals  (real program 071)
// Codeforces submission 628048, problem 108/A, MS C++, 2011-08-23
// https://codeforces.com/contest/108/submission/628048
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>
#include<string>
#include<vector>
#include<queue>
#include<stack>
#include<algorithm>
using namespace std;


int main()
{
    int h, m;
    scanf("%d:%d", &h, &m);

    int h1, h2;
    h2 = h % 10;
    h1 = h / 10;

    int back = h2 * 10 + h1; 

    if(h1 == 0)
    {
        if(h2 >= 6 || m >= back && h2 == 5)
        {
            printf("10:01\n");
            return 0;
        }
        if(back <= m)
            h2++;
        printf("0%d:%d0\n", h2, h2);
        return 0;
    }
    if(h1 == 1)
    {
        if(h2 >= 6 || m >= back && h2 == 5)
        {
            printf("20:02\n");
            return 0;
        }
        if(back <= m)
            h2++;
        printf("1%d:%d1\n", h2, h2);
        return 0;
    }
    if(h == 23 && m >= 32)
        printf("00:00\n");
    else
    {
        if(back <= m)
            h2++;
        printf("2%d:%d2\n", h2, h2);
        return 0;
    }

    return 0;
}
