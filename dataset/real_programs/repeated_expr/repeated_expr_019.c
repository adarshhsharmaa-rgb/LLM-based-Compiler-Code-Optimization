// category: repeated_expr  (real program 019)
// Codeforces submission 39842833, problem 997/B, C++14 (GCC 6-32), 2018-07-01
// https://codeforces.com/contest/997/submission/39842833
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main(void){
	long long int n;
	long long int ans=0;
	scanf("%lld",&n);
	for(int i=0;i<=8;i++){
		if(i==0){
			for(int j=0;j<=8;j++){
				if(n-i-j>=0){
					ans+=n-i-j+1;
				}
			}
		}
		else{
			for(int j=0;j<=4;j++){
				if(n-i-j>=0){
					ans+=n-i-j+1;
				}
			}
		}
	}
	printf("%lld\n",ans);
	
	return 0;
}
