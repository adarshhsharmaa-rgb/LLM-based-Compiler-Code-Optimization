// category: nested  (real program 014)
// Codeforces submission 13665551, problem 32/C, GNU C++, 2015-10-16
// https://codeforces.com/contest/32/submission/13665551
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <algorithm>
using namespace std;
int main(){
	int n,m,s;
	scanf("%d%d%d",&n,&m,&s);
	int a=(n-1)/s;
	int b=(m-1)/s;
	printf("%I64d",1ll*(n-s*a)*(m-s*b)*(a+1)*(b+1));
	return 0;
}
