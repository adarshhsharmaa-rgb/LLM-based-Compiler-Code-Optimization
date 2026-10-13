// category: nested  (real program 040)
// Codeforces submission 9936191, problem 387/A, GNU C++, 2015-02-20
// https://codeforces.com/contest/387/submission/9936191
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
using namespace std;
int main()
{
	int m1,m2,m3,h1,h2,h3;
	scanf("%d:%d",&h1,&m1);
	scanf("%d:%d",&h2,&m2);
	printf("%02d:%02d",(h1-h2-(m2>m1)+24)%24,(m1-m2+60)%60);
}
