// category: mixed  (real program 048)
// Codeforces submission 648096, problem 110/B, MS C++, 2011-08-29
// https://codeforces.com/contest/110/submission/648096
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main() {
	int n;
	scanf("%d",&n);
	int i;
	int a=0;
	for(i=1;i<=n;i++) {
		a++;
		printf("%c",'a'+a-1);
		if(a==4) a=0;
	}
}
