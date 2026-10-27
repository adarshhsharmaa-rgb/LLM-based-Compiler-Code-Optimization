// category: conditionals  (real program 074)
// Codeforces submission 15433970, problem 513/A, GNU C++, 2016-01-19
// https://codeforces.com/contest/513/submission/15433970
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
using namespace std;
int n,m;
int main() {
	scanf("%d%d",&n,&m);
	if (n<=m) puts("Second");
	else puts("First");
}
