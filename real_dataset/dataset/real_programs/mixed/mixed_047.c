// category: mixed  (real program 047)
// Codeforces submission 17305990, problem 488/A, GNU C++, 2016-04-13
// https://codeforces.com/contest/488/submission/17305990
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
long long int n,i,j,t;
int main(){
	scanf("%lld",&n);
	i=n;
	for(;;){
		i++;
		j=i;	
		while(j)
		if((j%10==8)||(-j%10==8)){
		    printf("%lld",i-n);
		    return 0;}
		    else 
		    j/=10;}
	return 0;}
