// category: loops  (real program 074)
// Codeforces submission 31656667, problem 877/C, GNU C++11, 2017-10-23
// https://codeforces.com/contest/877/submission/31656667
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio> 
#include<iostream> 
#include<vector>
#include<algorithm>
#include<cstring>
using namespace std;
int n;
int main()
{
	scanf("%d",&n);
	printf("%d\n",n/2+n);
	for(int i=2;i<=n;i+=2) printf("%d ",i);
	for(int i=1;i<=n;i+=2) printf("%d ",i);
	for(int i=2;i<=n;i+=2) printf("%d ",i);
}
