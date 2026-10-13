// category: arithmetic  (real program 055)
// Codeforces submission 33676346, problem 909/B, GNU C++11, 2017-12-27
// https://codeforces.com/contest/909/submission/33676346
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(){
	int n;
	int i;
	scanf("%d",&n);
	n++;
	i=n/2;
	printf("%d",i*(n-i));
	return 0;
}
