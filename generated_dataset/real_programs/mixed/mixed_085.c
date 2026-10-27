// category: mixed  (real program 085)
// Codeforces submission 17944679, problem 675/B, GNU C++11, 2016-05-16
// https://codeforces.com/contest/675/submission/17944679
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <string>
#include <cstring>
#include <cmath>
#include <iostream>
#include <algorithm>

using namespace std;

#define MAXN 100010
#define INF 0x3f3f3f3f
#define PI acos(-1.0)
typedef long long LL;

int main()
{
    int i,n,a,b,c,d,ans=0;
    int A,B,D,E;
    scanf("%d%d%d%d%d",&n,&a,&b,&c,&d);
    for(i=1;i<=n;++i){
        A=i;
        B=A+b-c;
        E=a+B-d;
        D=E+c-b;
        if(B>=1&&B<=n&&D>=1&&D<=n&&E>=1&&E<=n) ++ans;
    }
    printf("%I64d\n",1LL*ans*n);
}
