// category: loops  (real program 022)
// Codeforces submission 10485673, problem 509/A, GNU C++, 2015-03-27
// https://codeforces.com/contest/509/submission/10485673
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main(){
	int a;
	scanf("%d",&a);
	int s=1;
	for(int i=1;i<a;i++){
		s=s*(a*2-1-i)/i;
	}
	printf("%d\n",s);
	return 0;
}
