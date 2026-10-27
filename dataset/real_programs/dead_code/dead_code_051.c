// category: dead_code  (real program 051)
// Codeforces submission 22103874, problem 732/A, GNU C++, 2016-11-08
// https://codeforces.com/contest/732/submission/22103874
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>

#include <cstdio>

#include <algorithm>

#include <cstring>

using namespace std;

const int MAXN = 100000 + 5;

long long k,r;

int main()

{

	scanf("%d %d",&k,&r);

	for(int i = 1;i <= 10;i ++)

		if((k * i) % 10 == 0 || (k * i) % 10 == r)

		{

			printf("%d\n",i);

			return 0;

		}

	return 0;

}
