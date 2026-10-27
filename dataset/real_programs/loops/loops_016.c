// category: loops  (real program 016)
// Codeforces submission 31077195, problem 869/B, GNU C++, 2017-10-06
// https://codeforces.com/contest/869/submission/31077195
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#define ll long long
using namespace std;
int main()
{
    ll a,b,c,temp = 1;
    scanf("%I64d %I64d",&a,&b);
    for(ll i = b,j = 0;j < 10 && i > a; --i,++j)
    {
        c = i % 10;
        temp = temp * c % 10;
    }
    printf("%I64d\n",temp);
    return 0;
}
