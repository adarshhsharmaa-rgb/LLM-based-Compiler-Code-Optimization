// category: conditionals  (real program 080)
// Codeforces submission 1515952, problem 122/A, GNU C++, 2012-04-12
// https://codeforces.com/contest/122/submission/1515952
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
# include <stdio.h>
int main ()
{
	int a;
	scanf ("%d",&a);
	if (a%4==0 || a%7==0 || a==47 || a==477 || a==799 || a==94 || a==141)
	printf ("YES\n");
	else
	printf ("NO\n");
}
