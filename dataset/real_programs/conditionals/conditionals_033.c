// category: conditionals  (real program 033)
// Codeforces submission 60005239, problem 1214/B, GNU C++11, 2019-09-04
// https://codeforces.com/contest/1214/submission/60005239
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
#define ll long long
int main(){
	int b,g,n;
	scanf("%d %d %d",&b,&g,&n);
	if(n<=b&&n<=g){
		printf("%d",n+1);
	}else if(n>b&&n>g){
		printf("%d",b+g-n+1);
	}else if(n>b&&n<=g){
		printf("%d",b+1);
	}else{
		printf("%d",g+1);
	}
	return 0;
}
