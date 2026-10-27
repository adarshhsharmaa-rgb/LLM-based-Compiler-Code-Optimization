// category: mixed  (real program 081)
// Codeforces submission 16353033, problem 633/B, GNU C++11, 2016-02-26
// https://codeforces.com/contest/633/submission/16353033
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    int m;
    scanf("%d", &m);
    int k = 0, first = 0, last = -1;
    for(int i = 5; k <= m; i++)
    {
        int l = i;
        while(l % 5 == 0)
        {
            l /= 5;
            k++;
        }
        if(k == m)
        {
            if(first == 0) first = i;
            last = i;
        }
    }
    printf("%d\n", last - first + 1);
    for(int i = first; i <= last; i++)
        printf("%d ", i);
    puts("");
}
