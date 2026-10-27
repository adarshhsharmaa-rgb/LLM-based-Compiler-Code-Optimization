// category: mixed  (real program 007)
// Codeforces submission 17860352, problem 672/A, GNU C, 2016-05-11
// https://codeforces.com/contest/672/submission/17860352
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define pi 3.1415926


int main()
{

//int p = 1000;
//int s, n;
//for (s=1;s<p;++s)
//{
//    n = s;
    int n;
    scanf("%d", &n);

    int i, k, remain, results;
    if (n<10)
    {
        printf("%d",n);
        //continue;
        return 0;
    }
    if (n<190)
    {
        n = n - 9;
        k = n / 2;
        remain = n%2;
        results = 10 + k;
        if (!remain)
        {
            results -= 1;
        }
        if (remain)
        {
            for (i=0;i<(2-remain);++i)
            {
                results = results/10;
            }
        }
        results = results%10;
        printf("%d", results);
        //continue;
        return 0;
    }
    if (n<2701)
    {
        n = n - 189;
        k = n / 3;
        remain = n%3;
        results = 100 + k;
        if (!remain)
        {
            results -= 1;
        }
        if (remain)
        {
            for (i=0;i<(3-remain);++i)
            {
                results = results/10;
            }
        }
        results = results%10;
        printf("%d", results);
        //continue;
        return 0;
    }

//        n = n - 329;
//        k = n / 4;
//        remain = n%4;
//        results = 1000 + k;
//        if (!remain)
//        {
//            results -= 1;
//        }
//        if (remain)
//        {
//            for (i=0;i<(4-remain);++i)
//            {
//                results = results/10;
//            }
//        }
//        results = results%10;
//        printf("%d", results);
//        continue;
//        return 0;
//    }
    return 0;
}
