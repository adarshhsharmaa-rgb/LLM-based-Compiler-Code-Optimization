// category: conditionals  (real program 049)
// Codeforces submission 16783945, problem 606/A, GNU C++, 2016-03-18
// https://codeforces.com/contest/606/submission/16783945
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
using namespace std;
#include <cstdio>

main(){
    int a,b,c,x,y,z;
    scanf("%d %d %d %d %d %d",&a,&b,&c,&x,&y,&z);
    a-=x;
    b-=y;
    c-=z;
    if(a>-1)a/=2;
    if(b>-1)b/=2;
    if(c>-1)c/=2;
    if(a+b+c>-1)printf("Yes");
    else printf("No");
}
