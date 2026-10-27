// category: loops  (real program 056)
// Codeforces submission 39995766, problem 1004/B, GNU C++11, 2018-07-05
// https://codeforces.com/contest/1004/submission/39995766
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>

using namespace std;

int main() {
	int num_flowers;
	scanf("%d", &num_flowers);
	for (int i = 0; i < num_flowers; i++) {
		printf("%d", i % 2);
	}
	printf("\n");
	return 0;
}
