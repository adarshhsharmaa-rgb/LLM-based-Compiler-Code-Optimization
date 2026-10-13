// category: mixed  (real program 016)
// Codeforces submission 255860, problem 55/A, GNU C++, 2011-01-20
// https://codeforces.com/contest/55/submission/255860
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
using namespace std;
int main()
{
    int n,pr=1;
    scanf("%d",&n);
    while(pr<n)
        pr*=2;
    if(pr==n) printf("YES\n");
        else printf("NO\n");
    return 0;
}
