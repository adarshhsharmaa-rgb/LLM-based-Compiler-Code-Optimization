// category: loops  (real program 014)
// Codeforces submission 23441318, problem 750/A, MS C++, 2016-12-30
// https://codeforces.com/contest/750/submission/23441318
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){
	int n,k;
	scanf("%d%d",&n,&k);
	k=240-k;
	int i=0,num=0;
	while((i<=n)&&(num<=k)){
		i++;
		num+=5*i;
	};
	i--;
	printf("%d",i);
	return 0; 
}
