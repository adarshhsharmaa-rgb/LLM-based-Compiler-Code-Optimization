// category: mixed  (real program 072)
// Codeforces submission 165012106, problem 1667/C, C++20 (GCC 11-64), 2022-07-20
// https://codeforces.com/contest/1667/submission/165012106
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
/*

* Copyrights: OLE_OIer

* time: 2022/07/20 20:57

* Problem: CF1667C

*/

#include<bits/stdc++.h>

#define int long long

#define elif else if

using namespace std;

int n,k;

signed main(){

	scanf("%d",&n);

	k=(n*2+1)/3;

	printf("%d",k);

	for(int i=1,x=1;i<=k;++i,x+=2){

		if(x>k) x=2;

		printf("\n%d %d",x,i);

	}

	return 0;

}
