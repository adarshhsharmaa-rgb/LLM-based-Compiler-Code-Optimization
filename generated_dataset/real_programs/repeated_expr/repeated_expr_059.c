// category: repeated_expr  (real program 059)
// Codeforces submission 22209000, problem 622/B, MS C++, 2016-11-14
// https://codeforces.com/contest/622/submission/22209000
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>



int main()

{

	int h, m, a;

	scanf("%d:%d", &h, &m);

	scanf("%d", &a);



	printf("%02d:%02d", ((h * 60 + m + a) % (24 * 60)) / 60, ((h * 60 + m + a) % (24 * 60)) % 60);

	return 0;

}
