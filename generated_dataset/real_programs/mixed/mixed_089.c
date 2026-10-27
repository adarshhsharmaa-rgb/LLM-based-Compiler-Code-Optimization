// category: mixed  (real program 089)
// Codeforces submission 20885036, problem 651/A, GNU C++11, 2016-09-24
// https://codeforces.com/contest/651/submission/20885036
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main(){

	int x, y, s = 0;

	scanf("%d%d", &x, &y);

	while ( ( x > 1 || y > 1) && x && y){

		if ( x > y){

			s++;

			x -= 2;

			y++;

		} else if ( x <= y){

			s++;

			x++;

			y -= 2;

		}

	}

	printf("%d\n", s);

}
