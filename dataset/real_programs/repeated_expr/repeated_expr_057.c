// category: repeated_expr  (real program 057)
// Codeforces submission 614721, problem 85/A, GNU C++, 2011-08-18
// https://codeforces.com/contest/85/submission/614721
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
	int n;
	scanf("%d", &n);
	for (int j = 0; j < 2; ++j) {
		for (int i = 0; i < n / 2; ++i)
			printf("%c%c", 'a' + (j + i) % 2, 'a' + (j + i) % 2);
		if (n % 2 == 1) printf("%c", 'c');
		printf("\n");
	}
	for (int j = 0; j < 2; ++j) {
		printf("%c", 'd');
		for (int i = 0; i < (n - 1) / 2; ++i)
			printf("%c%c", 'e' + (j + i) % 2, 'e' + (j + i) % 2);
		if (n % 2 == 0) printf("%c", 'g');
		printf("\n");
	}
	return 0;
}
