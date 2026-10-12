// category: dead_code  (real program 029)
// Codeforces submission 33291930, problem 898/A, MS C++, 2017-12-16
// https://codeforces.com/contest/898/submission/33291930
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h> 
int main()
{
	int n, n1=0;
	scanf("%d", &n);
	if(n%10==0)
		printf("%d", n);
	else
		if(n%10>5)
	{
		n=(n/10+1)*10;
		printf("%d", n);
	}
	else
		if(n%10<=5)
	{
		n=n-n%10;
		printf("%d", n);
	}
}
