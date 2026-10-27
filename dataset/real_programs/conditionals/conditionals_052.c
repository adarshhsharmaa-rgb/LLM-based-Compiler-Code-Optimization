// category: conditionals  (real program 052)
// Codeforces submission 8673735, problem 476/A, GNU C++, 2014-11-12
// https://codeforces.com/contest/476/submission/8673735
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
using namespace std;
int main()
{
    int a,b;
    scanf("%d%d",&a,&b);
    b=((a+1)/2+b-1)/b*b;
    if(b>a)puts("-1");
    else printf("%d\n",b);
}
