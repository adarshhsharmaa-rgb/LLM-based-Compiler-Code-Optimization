// category: mixed  (real program 096)
// Codeforces submission 15115353, problem 611/B, GNU C++, 2015-12-30
// https://codeforces.com/contest/611/submission/15115353
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
int main()
{
	long long int a,b,n1=0,n2=0,ans;
	scanf("%lld %lld",&a,&b);
	long long b1=b,a1=a,z1=0,z2=0,pos1=-1,pos2=-1;
	while(a1!=0)
	{
		if(a1%2==0){
			z1++;
			pos1=n1;
		}
		a1=a1/2;
		n1++;
	}
	n1--;
	while(b1!=0)
	{
		if(b1%2==0){
			z2++;
			pos2=n2;
		}
		b1=b1/2;
		n2++;
	}
	n2--;
	if(z2==0)
		n2++;
	if(z1==0)
		n1++;
	long long t1,t2;
	t1=((n2)*(n2-1))/2;
	t2=((n1)*(n1-1))/2;
	ans=t1-t2;
	if(z2==1)
		ans++;
	if(pos1!=-1)
	ans=ans-(n1-pos1-1);
	if(pos2!=-1)
		ans=ans+(n2-pos2-1);
	printf("%lld\n",ans );
	return 0;
}
