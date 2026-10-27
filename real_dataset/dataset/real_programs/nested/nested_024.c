// category: nested  (real program 024)
// Codeforces submission 18180401, problem 630/R, GNU C++, 2016-06-01
// https://codeforces.com/contest/630/submission/18180401
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
long long n;
int main (){
	scanf("%I64d", &n);
	printf("%d\n", 1 + (n - 1) % 2);
	return 0;
}
