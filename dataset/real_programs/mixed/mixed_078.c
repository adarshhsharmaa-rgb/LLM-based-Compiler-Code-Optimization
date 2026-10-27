// category: mixed  (real program 078)
// Codeforces submission 21167819, problem 4/A, GNU C, 2016-10-03
// https://codeforces.com/contest/4/submission/21167819
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main()

{

	int w, i;

	scanf("%d", &w);

	if(w%2) printf("NO");

	else

	{

		for(i = 2; i <= w/2; i += 2)

		{

			if(!((w - i) % 2)){ printf("YES"); return 0; }

		}

		printf("NO");

	}

	return 0;

}
