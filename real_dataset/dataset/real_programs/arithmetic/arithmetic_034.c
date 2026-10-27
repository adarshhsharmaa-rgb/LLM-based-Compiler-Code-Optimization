// category: arithmetic  (real program 034)
// Codeforces submission 33290190, problem 898/A, GNU C++, 2017-12-16
// https://codeforces.com/contest/898/submission/33290190
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include"iostream"
#include"stdio.h"
#include"string.h"
using namespace std;

int main()
{
	int n;
	scanf("%d",&n);
	n+=5;
	n/=10;
	n*=10;
	printf("%d",n);
	return 0;
}
