// category: loops  (real program 018)
// Codeforces submission 9270595, problem 110/B, GNU C++, 2014-12-25
// https://codeforces.com/contest/110/submission/9270595
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main(){
	int n,i;
	scanf("%d",&n);
	for(i=0;i<n;i++) printf("%c",i%4+'a');
	printf("\n");
}
