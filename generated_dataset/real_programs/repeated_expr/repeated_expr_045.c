// category: repeated_expr  (real program 045)
// Codeforces submission 44810032, problem 1068/A, C++14 (GCC 6-32), 2018-10-24
// https://codeforces.com/contest/1068/submission/44810032
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;

int main(){
	
	long long n, m, k, l;
	scanf("%lld%lld%lld%lld", &n, &m, &k, &l);
	
	long long sum=(n/m)*m;
	if(m>n || sum-k<l){
		puts("-1");
		return 0;	
	}
	
	
	long long num =0;
	if( (l+k)%m == 0 ){
		num= (l+k)/m;
	}
	else{
		num= (l+k)/m +1;
	}
	
	printf("%lld\n", num);
		
	
	
	
	
	
	
	
	return 0;
}
