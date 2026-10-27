// category: conditionals  (real program 028)
// Codeforces submission 33309456, problem 898/A, GNU C++, 2017-12-16
// https://codeforces.com/contest/898/submission/33309456
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){
	int n;
	scanf("%d",&n);
	int c=n%10;
	n-=c;
	if(c>=5)n+=10;
	printf("%d\n",n);
	return 0;
}
