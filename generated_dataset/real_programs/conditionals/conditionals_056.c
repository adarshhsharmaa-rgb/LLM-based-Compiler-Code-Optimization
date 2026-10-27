// category: conditionals  (real program 056)
// Codeforces submission 18452153, problem 279/A, GNU C++, 2016-06-14
// https://codeforces.com/contest/279/submission/18452153
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include<stdio.h>
#include<algorithm>
using namespace std;

int x,y;
int main() {
	scanf("%d%d",&x,&y);
	int ans;
	if(x>=y&&(x+y)>1)
	ans=4*x-3;
	else if(x<y&&y>=-x)
	ans=4*y-2;
	else
	if(y<-x&&y>=x)
	ans=4*(-x)-1;
	else
	ans=4*(-y);
	
	printf("%d",ans);
	return 0;
}
