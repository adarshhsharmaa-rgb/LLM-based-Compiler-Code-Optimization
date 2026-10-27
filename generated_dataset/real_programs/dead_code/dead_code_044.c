// category: dead_code  (real program 044)
// Codeforces submission 3026842, problem 268/B, GNU C++, 2013-01-28
// https://codeforces.com/contest/268/submission/3026842
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

using namespace std;

int main(){
	int n;
	scanf("%d",&n);
	int count = n;
	int p = 1,t = 1;
	for(int i=1;i<=n-1;i++){
		p = 1;
		count = count + (n-i-1)+ (n-i-1)*i+1;	
	}
	printf("%d",count);


}
