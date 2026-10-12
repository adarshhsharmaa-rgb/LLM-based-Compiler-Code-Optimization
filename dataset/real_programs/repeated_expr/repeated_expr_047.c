// category: repeated_expr  (real program 047)
// Codeforces submission 21424312, problem 622/D, GNU C++11, 2016-10-14
// https://codeforces.com/contest/622/submission/21424312
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
int main(void){
	int n, i, nn;
	scanf("%d", &n);
	for(i = 1, nn=2; i < n; i+=2) printf("%d ", i);
	if(n%2){
		printf("%d ", n);
		nn--;
	}
	for(i -= 2; i > 0; i-=2) printf("%d ", i);
	for(i = 2; i < n; i+=2) printf("%d ", i);
	if(!(n%2)){
		printf("%d ", n);
		nn--;
	}
	for(i -= 2; i > 1; i-=2) printf("%d ", i);
	for(; nn; nn--) printf("%d ", n);
	printf("\n");
}
