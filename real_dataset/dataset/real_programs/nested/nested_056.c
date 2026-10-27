// category: nested  (real program 056)
// Codeforces submission 39616995, problem 996/A, GNU C, 2018-06-24
// https://codeforces.com/contest/996/submission/39616995
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
int main(){
	long long n;
	scanf("%I64d",&n);
	long long a = n/100;
	n = n-a*100;
	long long b = n/20;
	n = n-b*20;
	long long c = n/10;
	n = n- c*10;
	long long d = n/5;
	n = n-d*5;
	long long e = n;
	long long k = a+b+c+d+e;
	printf("%I64d\n",k);

}
