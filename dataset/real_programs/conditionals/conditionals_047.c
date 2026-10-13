// category: conditionals  (real program 047)
// Codeforces submission 31404289, problem 876/A, GNU C++11, 2017-10-16
// https://codeforces.com/contest/876/submission/31404289
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;

int main()
{
    int a,b,c,n,sum,sum1,count;
    scanf("%d%d%d%d",&n,&a,&b,&c);
    if(n>1){
        if(a<b) sum=a;
        else sum=b;
        if(sum>c) sum1=c;
        else sum1=sum;
        count=n-2;
        sum+=sum1*count;
        printf("%d\n",sum);
    }
    else printf("0\n");
    return 0;
}
