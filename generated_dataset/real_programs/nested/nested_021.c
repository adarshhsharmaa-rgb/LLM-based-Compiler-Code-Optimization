// category: nested  (real program 021)
// Codeforces submission 21267082, problem 669/A, C++14 (GCC 6-32), 2016-10-07
// https://codeforces.com/contest/669/submission/21267082
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;

int main()
{
	int n;
	scanf("%d",&n);
	
	printf("%d\n",(n/3)*2+(n%3>0));
	
	return 0;
}
