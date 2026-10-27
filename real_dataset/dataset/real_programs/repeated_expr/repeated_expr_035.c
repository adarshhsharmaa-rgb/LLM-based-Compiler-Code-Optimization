// category: repeated_expr  (real program 035)
// Codeforces submission 21080255, problem 722/A, C++14 (GCC 6-32), 2016-10-01
// https://codeforces.com/contest/722/submission/21080255
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

int main(){
	int a, b, n;
	scanf("%d", &n);
	scanf("%d:%d", &a, &b);
	if (b >= 60)
		b = b % 10;
	if (n == 24){
		if (a >= 24)	
			a = a % 10;
	}
	else{
		if (a > 12){
			if (a % 10 <= 2)
				a = 10 + a % 10;
			else
				a %= 10;
		}
		if (a == 0)
			a = 1;
	}
	printf("%02d:%02d\n", a, b);
	return 0;
}
