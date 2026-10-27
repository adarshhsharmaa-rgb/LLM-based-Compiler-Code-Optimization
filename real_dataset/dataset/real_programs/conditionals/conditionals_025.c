// category: conditionals  (real program 025)
// Codeforces submission 447474, problem 84/A, GNU C++, 2011-05-13
// https://codeforces.com/contest/84/submission/447474
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
#include<cstring>
using namespace std;
int main()
{
	int n;
	scanf("%d",&n);
	if(n==2) printf("3\n");
	else printf("%d\n",n/2*3);
	return 0;
}
