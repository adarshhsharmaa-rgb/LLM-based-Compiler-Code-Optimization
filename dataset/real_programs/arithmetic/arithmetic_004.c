// category: arithmetic  (real program 004)
// Codeforces submission 21621314, problem 622/B, GNU C++11, 2016-10-20
// https://codeforces.com/contest/622/submission/21621314
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

#include<cmath>

typedef long long ll;

int hour,minute,a;

int main(){

	scanf("%d:%d",&hour,&minute);

	scanf("%d",&a);

	minute+=a;

	int carry=minute/60;

	minute%=60;

	hour+=carry;

	hour%=24;

	printf("%02d:%02d\n",hour,minute);

}
