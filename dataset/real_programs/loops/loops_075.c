// category: loops  (real program 075)
// Codeforces submission 7993671, problem 333/A, GNU C++, 2014-09-28
// https://codeforces.com/contest/333/submission/7993671
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
typedef long long ll;
ll n,w;
int main(){
	scanf("%I64d",&n);
	for(w=1;n%w==0;w*=3);
	printf("%I64d\n",n/w+1);
}
