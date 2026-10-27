// category: mixed  (real program 055)
// Codeforces submission 17116582, problem 656/D, GNU C++, 2016-04-01
// https://codeforces.com/contest/656/submission/17116582
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<stdio.h>
#include<string.h>
#include<math.h>
#include<algorithm>
#include<map>
#include<vector>
using namespace std;
int n;
int main() {
	scanf("%d",&n);
	int res=0;
	while(n)
	{
		if(n%8==1)res++;
		n/=8;
	}
	printf("%d\n",res);
}
