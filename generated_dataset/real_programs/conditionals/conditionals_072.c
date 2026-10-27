// category: conditionals  (real program 072)
// Codeforces submission 39619117, problem 996/A, GNU C11, 2018-06-24
// https://codeforces.com/contest/996/submission/39619117
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
main()
{
	long int c=0,p=0,q=0,r=0,s,n,w,x1,x2,x3,x4;
	
	scanf("%ld",&n);
//	if(n==1||n==5||n==10||n==20||n==100)
	
	
	if(n>=100)
	{
		x1=n/100;
		n=n%100;
		c=c+x1;
	}
	if(n>=20&&n<100)
	{
		x2=n/20;
		n=n%20;
		p=p+x2;
	}
	if(n>=10&&n<20)
	{
		x3=n/10;
		n=n%10;
		q=q+x3;
	}
	if(n>=5&&n<10)
	{
		x4=n/5;
	  n=n%5;
	  r=r+x4;	
	}
	if(n>=1&&n<5)
	{
	   s=n;	
	}
  
	w=c+p+q+r+s;
	printf("%ld",w);
}
