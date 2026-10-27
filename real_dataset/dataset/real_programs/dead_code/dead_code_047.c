// category: dead_code  (real program 047)
// Codeforces submission 17236938, problem 660/B, GNU C++11, 2016-04-08
// https://codeforces.com/contest/660/submission/17236938
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include "stdio.h"
#include <algorithm>
#include <vector>
using namespace std;

int main()
{
	int n, m;
	int numseat; 
	int a, b;
	//freopen("Input.txt", "rt", stdin);
	scanf("%d%d", &n, &m);
	numseat = n*4;
	if(m <= n*2)
	{
		for(int i = 0; i < m; i++)
		{
			printf("%d ", i + 1);
		}
	}
	else
	{
		a = n*2 + 1;
		b = 1;
		for(int i = 0; i < m; i++)
		{
			if(a > m)
			{
				 printf("%d ", b);
				 b++;
			}
			else
			{
				printf("%d %d ", a, b);
				a++;
				b++;
				i++;
			}
		}
	}
	return 0;
}
