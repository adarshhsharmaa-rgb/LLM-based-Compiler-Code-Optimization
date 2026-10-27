// category: loops  (real program 009)
// Codeforces submission 39618857, problem 996/A, GNU C++, 2018-06-24
// https://codeforces.com/contest/996/submission/39618857
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
int A = 0;
int count = 0;

using namespace std;

int main()
{
	scanf("%d", &A);

	while (A >= 100) {		
		A -= 100;
		count++;			
	}
	
	while (A >= 20) {		
		A -= 20;
		count++;			
	}
	
	while (A >= 10) {		
		A -= 10;
		count++;			
	}
	
	while (A >= 5) {		
		A -= 5;
		count++;			
	}
	
	while (A >= 1) {		
		A -= 1;
		count++;			
	}
	
	printf("%d", count);
	
	return 0;
}
