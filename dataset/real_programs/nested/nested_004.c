// category: nested  (real program 004)
// Codeforces submission 17365859, problem 628/A, GNU C++, 2016-04-17
// https://codeforces.com/contest/628/submission/17365859
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int n,b,p;

int main(){
	scanf("%d %d %d",&n,&b,&p);
	printf("%d %d",(n-1)*(2*b+1),n*p);
	return 0;
}
