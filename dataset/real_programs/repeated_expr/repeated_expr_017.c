// category: repeated_expr  (real program 017)
// Codeforces submission 593308, problem 104/A, GNU C++, 2011-08-07
// https://codeforces.com/contest/104/submission/593308
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstdlib>
#include <algorithm>

int main(void)
{
	int n ;
	scanf("%d" , &n) ;
	
	if(n - 10 <= 0) puts("0") ;
	else if(n - 10 >= 1 && n - 10 < 10) puts("4") ;
	else if(n - 10 == 10) puts("15") ;
	else if(n - 10 == 11) puts("4") ;
	else puts("0") ;
	
	return 0 ;
}
