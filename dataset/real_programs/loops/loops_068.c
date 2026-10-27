// category: loops  (real program 068)
// Codeforces submission 41344948, problem 1017/C, C++17 (GCC 7-32), 2018-08-08
// https://codeforces.com/contest/1017/submission/41344948
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include "stdio.h"
#include <vector>
#include <algorithm>
#include "memory.h"
#include <set>

using namespace std;

int main() {
	int n;
	scanf("%d", &n);
	int s = 0;
	while (s*s < n) s++;
	for (int i = s-1; i >= 0; i--) {
		for (int j = (n*i) / s; j < (n*(i + 1)) / s; j++) printf("%d ", j + 1);
	}
	printf("\n");
	return 0;
}
