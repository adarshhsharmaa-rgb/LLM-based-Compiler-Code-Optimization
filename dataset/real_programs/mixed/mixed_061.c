// category: mixed  (real program 061)
// Codeforces submission 36998790, problem 934/B, GNU C++, 2018-04-05
// https://codeforces.com/contest/934/submission/36998790
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{

    int k;
    scanf("%d",&k);
    if(k>36)puts("-1");
    else
    {

        for(int i=0;i<k/2;i++)
            printf("8");
        if(k%2)
            printf("6");
        printf("\n");
    }return 0;
}
