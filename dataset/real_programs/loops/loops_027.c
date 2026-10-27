// category: loops  (real program 027)
// Codeforces submission 13452725, problem 584/B, GNU C++, 2015-10-06
// https://codeforces.com/contest/584/submission/13452725
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
long long pp,a,doi,sapte,doisapte,n,i,ras,p;
int main()
{
    //freopen("p2.ib","r",stdin);
    //freopen("p2.out","w",stdout);
    scanf("%I64d",&n);
    a=1;
    for(i=1;i<=9;i++)
        a=a*10;
    a=a+7;
    ras=20;
    pp=7;
    for(i=2;i<=n;i++)
    {
        ras=ras*27%a+20*pp%a;
        pp=pp*7%a;
    }
    ras=ras%a;
    printf("%I64d",ras);
    return 0;
}
