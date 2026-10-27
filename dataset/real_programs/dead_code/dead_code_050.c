// category: dead_code  (real program 050)
// Codeforces submission 4120010, problem 329/D, GNU C++, 2013-07-20
// https://codeforces.com/contest/329/submission/4120010
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <vector>
using namespace std;

#define FOR(it, c) for(__typeof((c).begin()) it = (c).begin(); it != (c).end(); it++)
#define SZ(c) ((int)(c).size())

int main(void) {
	int n, x;
	scanf("%d%d", &n, &x);
	if(n==5) printf(">...v\nv.<..\n..^..\n>....\n..^.<\n1 1\n");
	if(n==3) printf(">vv\n^<.\n^.<\n1 3\n");
	if(n==100) {
		for(int i=0;i<50;i++) {
			puts("v<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");
			puts(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>.>^");
		}
		printf("1 1\n");
	}
	return 0;
}
