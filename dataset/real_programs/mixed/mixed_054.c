// category: mixed  (real program 054)
// Codeforces submission 19587580, problem 626/C, GNU C++, 2016-08-02
// https://codeforces.com/contest/626/submission/19587580
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main(){
	int n,m,r,q;
	scanf("%d%d",&n,&m);
	for(r=2,q=0;q<m+n;++r){
		if(r%6==0)q++;
		else {
			if(n&&r%2==0)n--;
			if(m&&r%3==0)m--;
		}
	}
	printf("%d\n",r-1);
	return 0;
}
