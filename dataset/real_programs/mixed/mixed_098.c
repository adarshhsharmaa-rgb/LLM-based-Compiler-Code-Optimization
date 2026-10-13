// category: mixed  (real program 098)
// Codeforces submission 19141581, problem 690/A2, GNU C++11, 2016-07-15
// https://codeforces.com/contest/690/submission/19141581
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

#include <cmath>



int main(){

	long n;

	scanf("%ld", &n);

	if(n%2)printf("%ld\n", (n-1)/2);

	else{

		long tmp = 1;

		while(tmp*2<=n)tmp*=2;

		printf("%ld\n", (n-tmp)/2);

	}



}
