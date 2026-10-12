// category: loops  (real program 061)
// Codeforces submission 22235322, problem 734/B, C++14 (GCC 6-32), 2016-11-15
// https://codeforces.com/contest/734/submission/22235322
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(){
	long int k2,k3,k5,k6;
	long long int total;
	scanf("%ld %ld %ld %ld",&k2,&k3,&k5,&k6);
	total=0;	
		while(k2>0 && k5>0 && k6>0){
			total+=256;
			k2--;k5--;k6--;
		}
		while (k2>0 && k3 >0){
			total+=32;
			k2--;k3--;
		}
		
	printf("%lld",total);	
	
	return 0;
}
