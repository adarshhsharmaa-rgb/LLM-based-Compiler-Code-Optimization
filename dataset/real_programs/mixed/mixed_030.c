// category: mixed  (real program 030)
// Codeforces submission 39904565, problem 1003/B, GNU C++, 2018-07-03
// https://codeforces.com/contest/1003/submission/39904565
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>//CF1003B
#include<iostream>
#include<algorithm>
#include<set>
#include<vector>
#include<queue>
#include<string>
#include<cstring>
#include<cstdlib>
#include<cmath>

using namespace std;

int a,b,x,f,n;

int main(){
	scanf("%d%d%d",&a,&b,&x);
	n=a+b;
	if(a<b){
		f=1;
	}
	for(int i=1;i<=n;i++){
		printf("%d",f);
		if(f==0){
			a--;
		}
		if(f==1){
			b--;
		}
		if(x>1){
			f=1-f;
			x--;
		}
		if(x==1&&(a==0||b==0)){
			f=1-f;
			x--;
		}
	}
	return 0;
}
