// category: mixed  (real program 032)
// Codeforces submission 20282698, problem 584/A, GNU C++, 2016-08-30
// https://codeforces.com/contest/584/submission/20282698
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>

#include <stdio.h>

#include <cmath>



using namespace std;

int main()

{

	int n = 0, t = 0, i = 0;

	scanf("%d %d",&n,&t);

	if (n == 1 && t == 10)

		printf("%d", -1);

	else

		if ( t != 10)

			for ( i = 0; i < n; i++)

				printf("%d", t);

		else

			{

				for (i = 0; i < n - 1; i++)

					printf("%d", 1);

				printf("%d", 0);

			}			

	return 0;

}
