// category: dead_code  (real program 006)
// Codeforces submission 21583248, problem 732/C, GNU C++, 2016-10-19
// https://codeforces.com/contest/732/submission/21583248
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

#include <cstdlib>

#include <cstring>

#include <algorithm>

#include <cmath>



using namespace std;



const int maxn = 1000010;



int main() {

	long long b;

	scanf("%I64d", &b);

	long long d;

	scanf("%I64d", &d);

	long long s;

	scanf("%I64d", &s);



	if (b == d && b == s) {

		printf("%I64d\n", 0);

	}

	if (b == d && d > s) {

		printf("%I64d\n", d - 1 - s);

	}

	if (d == s && s > b) {

		printf("%I64d\n", s - 1 - b);

	}

	if (s == b && b > d) {

		printf("%I64d\n", b - 1 - d);

	}

	if (b > d && b > s) {

		printf("%I64d\n", b - 1 - d + b - 1 - s);

	}

	if (d > s && d > b) {

		printf("%I64d\n", d - 1 - s + d - 1 - b);

	}

	if (s > b && s > d) {

		printf("%I64d\n", s - 1 - b + s - 1 - d);

	}



	return 0;

}
