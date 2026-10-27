// category: arithmetic  (real program 049)
// Codeforces submission 972365, problem 125/A, GNU C++, 2011-12-23
// https://codeforces.com/contest/125/submission/972365
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cmath>
int main(){
	int cm;
	scanf ("%d",&cm);

	int inch = (cm+1)/3;
	
	printf ("%d %d\n",inch/12,inch%12);
	
	return 0;

}
