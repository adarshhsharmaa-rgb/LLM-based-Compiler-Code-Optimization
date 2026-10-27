// category: arithmetic  (real program 054)
// Codeforces submission 20086551, problem 678/A, GNU C++, 2016-08-23
// https://codeforces.com/contest/678/submission/20086551
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

using namespace std;



int main()

{

	long long int n, k;

	scanf("%I64d %I64d", &n, &k);

	n = n/k+1;

	printf("%I64d\n", n*k);

}
