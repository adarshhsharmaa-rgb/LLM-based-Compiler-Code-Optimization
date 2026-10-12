// category: arithmetic  (real program 059)
// Codeforces submission 16707331, problem 622/B, GNU C++, 2016-03-14
// https://codeforces.com/contest/622/submission/16707331
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cstdio>

int main()
{
	int h, m;
	int num;
	scanf("%d:%d", &h, &m);
	scanf("%d", &num);
	m += num;
	h += m / 60;
	printf("%02d:%02d\n", h % 24, m % 60);
	return 0;
}
