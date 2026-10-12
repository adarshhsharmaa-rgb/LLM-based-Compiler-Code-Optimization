// category: repeated_expr  (real program 058)
// Codeforces submission 21266554, problem 401/C, C++14 (GCC 6-32), 2016-10-07
// https://codeforces.com/contest/401/submission/21266554
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>

#include<stdio.h>

#include<set>

#include<algorithm>

#include<queue>

#include<memory.h>

#include<vector>

#include<string>

using namespace std;

int main(){

	int n, m, x;

	scanf("%d%d", &n, &m);

	bool ok=true;

	if (m >= n-1 && m <= n * 2 + 2)

	{ 

		x = m - (n + 1);

		if(n == m+1)ok=false;

		for (int i = 0; i < n ; i++)

		{

			if (x > 0){ printf("%d", 11); x--; }

			else if(ok)printf("%d", 1);

			printf("%d", 0);

			ok=true;

		}

		if (x > 0){ printf("%d", 11); x--; }

		else if( n!=m && n != m+1)printf("%d", 1);

	}

	else printf("%d",-1);

	return 0;

}
