// category: loops  (real program 080)
// Codeforces submission 5486776, problem 171/A, GNU C++, 2013-12-21
// https://codeforces.com/contest/171/submission/5486776
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int a,b,c = 0;
int main(){
	scanf("%d%d",&a,&b);
	while (b){
		c =  c * 10 + b % 10;
		b /= 10;
	}
	printf("%d\n",a + c);
}
