// category: mixed  (real program 009)
// Codeforces submission 20176695, problem 534/B, GNU C++11, 2016-08-26
// https://codeforces.com/contest/534/submission/20176695
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>



main() {

	int v1, v2, t, d;

	scanf("%d%d%d%d", &v1, &v2, &t, &d);

	int ans = v1 + v2, mx = 0;

	for (int i = 2; i < t; i++) {

		mx = v2 + d * (t - i);

		v1 = v1 + d;

		if (v1 > mx)

			v1 = mx;

		ans += v1;

	}

	printf("%d", ans);

}
