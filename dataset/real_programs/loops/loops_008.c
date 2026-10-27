// category: loops  (real program 008)
// Codeforces submission 43779083, problem 1060/B, GNU C11, 2018-10-04
// https://codeforces.com/contest/1060/submission/43779083
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main  () {
	long long n,a,b,s=0,t=1,a1,s1=0,t1,n1;
	scanf("%lld",&n);
	n1=n;
	while(n>0){
		n=n/10;
		t++;
	}
	t=t-2;
//	printf("%lld\n",t);
	t1=t;
	while(t>0){
		t--;
		s=s*10+9;
	}
	a=n1-s;
//	printf("%lld %lld \n",a,s);
	while(a>0){
		a1=a%10;
		s1=s1+a1;
		a=a/10;
	}
//	printf ("%lld %lld\n",s1,t1);
	printf("%lld",s1+9*t1);
}
