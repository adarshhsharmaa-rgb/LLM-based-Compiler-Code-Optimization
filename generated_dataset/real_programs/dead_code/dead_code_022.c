// category: dead_code  (real program 022)
// Codeforces submission 3681253, problem 301/C, GNU C++, 2013-05-05
// https://codeforces.com/contest/301/submission/3681253
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<string.h>
#include<iostream>
#include<queue>
#include<algorithm>
using namespace std;

const int maxn=200010;

int main()
{
	int i,j,k;
	for(i=0;i<=9;i++)
		printf("?1%d>>%d?1\n",i,i);
	puts("?1>>?");
	for(i=0;i<9;i++)
		printf("%d?<>%d\n",i,i+1);
	puts("9?>>?0");
	puts("?<>1");
	for(i=0;i<=9;i++)
		printf("%d>>?1%d\n",i,i);
}
