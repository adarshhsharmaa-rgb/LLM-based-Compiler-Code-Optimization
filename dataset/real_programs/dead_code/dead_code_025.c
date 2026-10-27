// category: dead_code  (real program 025)
// Codeforces submission 15935495, problem 622/B, GNU C++, 2016-02-10
// https://codeforces.com/contest/622/submission/15935495
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

typedef long long LL;
using namespace std;
const int M = 1000000007;

int main()
{
int a,b,c;

scanf("%d:%d %d",&a,&b,&c);

a=(a+((b+c)/60))%24;
b=(b+c)%60;

if(a<10)
	printf("0%d:",a);
else
	printf("%d:",a);

if(b<10)
	printf("0%d\n",b);
else
	printf("%d\n",b);

	

}
