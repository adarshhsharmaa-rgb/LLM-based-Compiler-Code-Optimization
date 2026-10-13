// category: loops  (real program 062)
// Codeforces submission 4443121, problem 110/B, GNU C++, 2013-09-11
// https://codeforces.com/contest/110/submission/4443121
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

int main(){
	int n;
	scanf("%d",&n);
	for(int i=0;i<n;i++)
		printf("%c",i%4+'a');
	printf("\n");
	return 0;
}
