// category: conditionals  (real program 026)
// Codeforces submission 17949041, problem 675/A, GNU C++11, 2016-05-16
// https://codeforces.com/contest/675/submission/17949041
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>
#include <vector>
using namespace std;

int main(void)
{
	int a, b, c;
	scanf("%d%d%d", &a, &b, &c);
	bool don = false;
	if(c == 0)
	{
		if(b == a)
		{
			printf("YES\n"); return 0;
		}
		else
		{
			printf("NO\n"); return 0;
		}
	}
	if((b-a)%c == 0)
	{
		if(b >= a && c >= 0) don = true;
		else if(b <= a && c < 0) don = true;
	}
	if(!don) printf("NO\n");
	else printf("YES\n");
}
