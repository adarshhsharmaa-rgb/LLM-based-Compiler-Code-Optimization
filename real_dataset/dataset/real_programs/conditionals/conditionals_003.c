// category: conditionals  (real program 003)
// Codeforces submission 11948568, problem 122/A, GNU C++, 2015-07-06
// https://codeforces.com/contest/122/submission/11948568
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
# include <stdio.h>
int main ()
{
	int x;
	scanf ("%d",&x);
	if (x%4==0 || x%7==0 || x%47==0 || x%74==0 || x%477==0)
	printf ("YES\n");
	else
	printf ("NO\n");
}
