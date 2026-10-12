// category: repeated_expr  (real program 060)
// Codeforces submission 41368474, problem 1017/C, C++17 (GCC 7-32), 2018-08-08
// https://codeforces.com/contest/1017/submission/41368474
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <set>
#include <map>
#include <queue>
#include <deque>
#include <cmath>
#include <stack>
#include <cstdio>
#include <vector>
#include <string>
#include <bitset>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <fstream>
#include <iostream>
#include <algorithm>
#define ll long long
#define pii pair <int, int>
#ifdef DEBUG
	#define LLD "%lld"
#else
	#define LLD "%I64d"
#endif
using namespace std;

int main() {
	int n; scanf("%d", &n);
	int mn = (n + 1) / 2 + 2, mnx = 2;
	for (int x = 3; x <= n; ++ x) {
		int nw = (n + x - 1) / x + x;
		if (nw < mn) {
			mn = nw;
			mnx = x;
		}
	}
	for (int i = n / mnx * mnx + 1; i <= n; ++ i) printf("%d ", i);
	for (int i = n / mnx; i > 0; -- i) {
		for (int j = i * mnx - mnx + 1; j <= i * mnx; ++ j) printf("%d ", j);
	}
	return 0;
}
