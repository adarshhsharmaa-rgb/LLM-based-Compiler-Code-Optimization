// category: repeated_expr  (real program 034)
// Codeforces submission 21006710, problem 271/A, C++14 (GCC 6-32), 2016-09-30
// https://codeforces.com/contest/271/submission/21006710
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>



using namespace std;







int main()

{

	//freopen("input.txt","r",stdin);

	//freopen("output.txt","w",stdout);

	int y, n, a, b, c, d;

	scanf("%d", &y);

	n = y + 1;

	while(1) {

		y = n;

		a = y %10;

		y /= 10;

		b  = y % 10;

		y /= 10;

		c = y%10;

		y /= 10;

		d = y;

		if(a != b && a != c && a != d && b != c && b != d && c != d) {

			printf("%d",n);

			return 0;

		}

		n++;



	}

}
