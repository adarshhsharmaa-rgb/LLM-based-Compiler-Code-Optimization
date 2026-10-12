// category: mixed  (real program 088)
// Codeforces submission 31405400, problem 876/A, GNU C++11, 2017-10-16
// https://codeforces.com/contest/876/submission/31405400
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
/*
* @Author: lyucheng
* @Date:   2017-10-16 18:38:12
* @Last Modified by:   lyucheng
* @Last Modified time: 2017-10-16 20:18:01
*/
#include <bits/stdc++.h>

using namespace std;

int n,a,b,c;
int pos;
int res;
int val;

int main(){
	// freopen("in.txt","r",stdin);
	scanf("%d%d%d%d",&n,&a,&b,&c);
	pos=1;
	res=1;
	val=0;
	while(res<n){
		res++;
		if(pos==1){
			if(a<b){
				pos=2;
				val+=a;
			}else{
				pos=3;
				val+=b;
			}
		}else if(pos==2){
			if(a<c){
				pos=1;
				val+=a;
			}else{
				pos=3;
				val+=c;
			}
		}else if(pos==3){
			if(b<c){
				pos=1;
				val+=b;
			}else{
				pos=2;
				val+=c;
			}
		}	
	}
	printf("%d\n",val);
	return 0;
}
