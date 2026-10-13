// category: dead_code  (real program 048)
// Codeforces submission 43971886, problem 1033/A, GNU C++11, 2018-10-07
// https://codeforces.com/contest/1033/submission/43971886
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    int n,ax,ay,bx,by,cx,cy;
    scanf("%d %d%d %d%d %d%d",&n,&bx,&by,&ax,&ay,&cx,&cy);
    if(!((ax<bx && bx<cx) || (ax>bx && bx>cx) || (ay<by && by<cy) || (ay>by && by>cy)))
        printf("YES");
    else
        printf("NO");
}
