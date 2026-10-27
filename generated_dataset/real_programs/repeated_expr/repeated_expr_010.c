// category: repeated_expr  (real program 010)
// Codeforces submission 17611055, problem 472/A, GNU C++, 2016-05-01
// https://codeforces.com/contest/472/submission/17611055
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
main() {
	int n;
	scanf("%d",&n);
	if(n%2==0) printf("%d %d",n-4,n-(n-4));
	else printf("%d %d",n-9,n-(n-9));
}
