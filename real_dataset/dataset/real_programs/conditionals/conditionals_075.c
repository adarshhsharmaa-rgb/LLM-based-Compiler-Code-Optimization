// category: conditionals  (real program 075)
// Codeforces submission 2105544, problem 168/A, GNU C++, 2012-09-09
// https://codeforces.com/contest/168/submission/2105544
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main(){
	int n,x,y,ans;
	scanf("%d%d%d",&n,&x,&y);
	ans=(n*y-1)/100-x+1;
	if(ans<0){ans=0;}
	printf("%d\n",ans);
	return 0;
}
