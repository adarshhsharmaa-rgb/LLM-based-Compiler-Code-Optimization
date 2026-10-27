// category: dead_code  (real program 003)
// Codeforces submission 16002517, problem 626/C, GNU C++, 2016-02-13
// https://codeforces.com/contest/626/submission/16002517
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
//8 VC C
//author: Jaydeep Khandelwal
#include<bits/stdc++.h>
using namespace std;

#define ll long long
#define mod 1000000007


int main()
{
	ll t,i=0,j,k,x,y,z,count=0,p,flag=0,ans=0,sum=0,l,n,max1,max2,m,p1,p2;
	
	scanf("%I64d%I64d",&n,&m);
	
//	scanf("%s",s);
	
	int ans1=0,ans2=0;
	
	if(m==0)
	ans=2*n;
	
	else if(n==0)
	ans=3*m;
	
	
	else
	{
	    max1=2*n;
	    max2=3*m;
	    
	    if(m%2==0)
	        p=1;
	    else
	        p=0;
	    
	    for(i=6;i<=max1 && i<=max2;i+=6)
	    {
	            if(p==1)
	           {
	               p2=max2+3;
	               
	           }
	        
	        else
	        p2=max2+3;
	        
	       p1=max1+2;
	            
	            if(p1>p2)
	            {
	            max2=p2;
	            p=0;
	            }
	            else
	            max1=p1;
	    // 	    printf("%I64d %I64d ",max1,max2);
   
	    }
	    
	    
	    
	    if(max1>max2)
	    ans=max1;
	    
	    else
	    ans=max2;
	    
	    
	    
	    
	}
	
	
	
	
	
	
	
	
    printf("%I64d\n",ans);
    
    
    
    
	return 0;
}
