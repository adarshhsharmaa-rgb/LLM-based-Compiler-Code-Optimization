// category: dead_code  (real program 001)
// Codeforces submission 44298079, problem 1064/A, C++14 (GCC 6-32), 2018-10-14
// https://codeforces.com/contest/1064/submission/44298079
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int a,b,c,i,res=0;
int main()
{
    scanf ("%d %d %d",&a,&b,&c);
    if ( a+b > c && a+c > b && b+c > a )
        printf("0");
    else
    {
        if ( a>b && a>c ) printf("%d",a-b-c+1);
        if ( b>c && b>a ) printf("%d",b-a-c+1);
        if ( c>a && c>b ) printf("%d",c-a-b+1);
    }
}
