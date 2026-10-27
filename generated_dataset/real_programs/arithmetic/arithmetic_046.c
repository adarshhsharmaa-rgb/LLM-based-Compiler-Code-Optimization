// category: arithmetic  (real program 046)
// Codeforces submission 33678293, problem 909/B, GNU C++11, 2017-12-27
// https://codeforces.com/contest/909/submission/33678293
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<cstring>
#include<iostream>
#include<algorithm>
#include<cmath>
using namespace std;

int n;

int main()
{
    scanf("%d",&n);
    int a=n/2;
    int b=n-a;
    printf("%d\n",(a+1)*b);
    return 0;
}
