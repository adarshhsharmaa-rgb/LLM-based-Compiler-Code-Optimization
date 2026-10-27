// category: dead_code  (real program 027)
// Codeforces submission 44626205, problem 1031/A, GNU C++11, 2018-10-21
// https://codeforces.com/contest/1031/submission/44626205
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<string>
#include<cstring>
using namespace std;
const int maxn=105;
int n,m,k;
int main(){
	scanf("%d%d%d",&n,&m,&k);
	int ans=0;
	for (int i=1;i<=k;i++){
		int x=2*i-1;
		ans+=(n-2*x+2)*2+(m-2*x+2)*2-4;
	}
	printf("%d\n",ans);
	return 0;
}
