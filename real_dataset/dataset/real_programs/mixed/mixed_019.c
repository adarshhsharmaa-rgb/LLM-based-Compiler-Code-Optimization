// category: mixed  (real program 019)
// Codeforces submission 18491185, problem 681/B, GNU C++, 2016-06-15
// https://codeforces.com/contest/681/submission/18491185
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

const int a=1234567,b=123456,c=1234;
int n;
int main(){
	scanf("%d",&n);
	for(int i=0;i<=n;i+=a)
		for(int j=i;j<=n;j+=b)
			if((n-j)%c==0) { puts("YES"); return 0; }
	puts("NO");
	return 0;
}
