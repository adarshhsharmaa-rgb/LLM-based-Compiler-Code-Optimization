// category: conditionals  (real program 001)
// Codeforces submission 340675, problem 68/A, GNU C++, 2011-03-18
// https://codeforces.com/contest/68/submission/340675
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <algorithm>
using namespace std;

int main(void)
{
	int a, b, c, d, e, f;
	scanf("%d%d%d%d%d%d", &a, &b, &c, &d, &e, &f);
	if(a>b) a=b;
	if(a>c) a=c;
	if(a>d) a=d;
	if(f>=a) f=a-1;
	if(e>f) e=f+1;
	printf("%d\n", f-e+1);
	return 0;
}
