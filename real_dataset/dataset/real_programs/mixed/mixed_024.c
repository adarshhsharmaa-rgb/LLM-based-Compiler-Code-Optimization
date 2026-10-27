// category: mixed  (real program 024)
// Codeforces submission 15475007, problem 620/A, GNU C++, 2016-01-21
// https://codeforces.com/contest/620/submission/15475007
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
using namespace std;
int main()
{
    int x1,y1,y2,x2,cx=0,cy=0;
    scanf("%d%d%d%d",&x1,&y1,&x2,&y2);
    if(x1>x2)
    {
        while(x1!=x2)
        {
            x1--;
            cx++;
        }
    }
    else
    {
        while(x1!=x2)
        {
            x1++;
            cx++;
    }
    }
    if(y1>y2)
    {
        while(y1!=y2)
        {
            y1--;
            cy++;
        }
    }
    else
    {
        while(y1!=y2)
        {
            y1++;
            cy++;
        }
    }
    if(cy>cx)
    {
        printf("%d",cy);
    }
    else
    {
        printf("%d",cx);
    }
}
