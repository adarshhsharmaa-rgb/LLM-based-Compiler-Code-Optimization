// category: conditionals  (real program 043)
// Codeforces submission 17939685, problem 675/B, GNU C++, 2016-05-16
// https://codeforces.com/contest/675/submission/17939685
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
#include <cstring>
#include <algorithm>

using namespace std;

long long n,a,b,c,d,ans,k1,k2;

int main() {
	scanf("%I64d %I64d %I64d %I64d %I64d",&n,&a,&b,&c,&d);
	k1=a-d;
	k2=b-c;
	if (k1<0) k1=-k1;
	if (k2<0) k2=-k2;
	ans=k1+k2;
	if (ans>=n) printf("0\n");
	else {
		printf("%I64d\n",(n-ans)*n);
	}
	return 0;
}
