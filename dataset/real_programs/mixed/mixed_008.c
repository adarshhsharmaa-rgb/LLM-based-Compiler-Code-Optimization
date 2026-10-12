// category: mixed  (real program 008)
// Codeforces submission 15119998, problem 611/B, GNU C++11, 2015-12-30
// https://codeforces.com/contest/611/submission/15119998
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#include<iostream>
using namespace std;
long long l,r,num=1,tot=1,x=1,num2=0,ans=0;
int main()
{
   scanf("%I64d %I64d",&l,&r);
   for(int i=2;i<=1000;i++)
   {
   	  tot*=2;
   	  num+=tot;
	  for(int j=1;j<=i-1;j++)
   	  {
   	  	for(int k=2;k<=j;k++)
   	    {
   	  	   x*=2;
   	    }
   	    num2=num-x;
   	    if(num2>=l&&num2<=r) ans++;
	    x=1;
   	  }
   	  if(num2>r)
	    {
	    	printf("%I64d",ans);
	    	return 0;
	    }
   }
   return 0;
}
