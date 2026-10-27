// category: arithmetic  (real program 031)
// Codeforces submission 15839612, problem 617/A, GNU C++, 2016-02-06
// https://codeforces.com/contest/617/submission/15839612
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
	int n;
	scanf("%d",&n);
	printf("%d\n",n/5+(n%5>0));
	return 0;
}
