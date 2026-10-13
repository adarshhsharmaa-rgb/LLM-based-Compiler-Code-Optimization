// category: nested  (real program 023)
// Codeforces submission 21848239, problem 678/A, MS C++, 2016-10-28
// https://codeforces.com/contest/678/submission/21848239
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

#include <cmath>



int main()

{

	int n,k;

	scanf("%d %d", &n, &k);



	printf("%d", (n / k + 1) * k);

	return 0;

}
