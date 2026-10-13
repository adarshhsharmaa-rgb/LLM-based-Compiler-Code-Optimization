// category: loops  (real program 079)
// Codeforces submission 2483655, problem 241/G, GNU C++, 2012-11-01
// https://codeforces.com/contest/241/submission/2483655
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>

using namespace std;

int n = 35000;

int main() {
	puts("302\n0 500000\n");
	for (int i = 300; i > 0; i--) {
		printf("%d %d\n", n, i);
		n += 2 * i - 1;
	}
	puts("999997 500000");
	return 0;
}
