// category: dead_code  (real program 002)
// Codeforces submission 36949119, problem 922/A, GNU C++, 2018-04-04
// https://codeforces.com/contest/922/submission/36949119
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<cstring>
#include<cstdlib>
#include<iostream>
#include<algorithm>
using namespace std;
int x,y,xnum=0,ynum=0;
int main()
{
 
 scanf("%d%d",&y,&x);
 if(x==1&&y>0||x==0)
    {
        printf("No");
        return 0;
    }
    int z=x-1;
    y-=z;
    if(y>=0&&y%2==0) printf("Yes");
           else  printf("No");
    return 0;
}
