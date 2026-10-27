// category: repeated_expr  (real program 003)
// Codeforces submission 22150345, problem 450/B, C++14 (GCC 6-32), 2016-11-10
// https://codeforces.com/contest/450/submission/22150345
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;



int main() 

{

    long long int n,x,y,a=0,b=0,c=0,d=0,e=0,f=0;

    scanf("%lld%lld",&x,&y);

    scanf("%lld",&n);

    a=x;

    b=y;

    c=b-a;

    d=-1*x;

    e=-1*y;

    f=-1*c;

    a=a%1000000007;

    b=b%1000000007;

    c=c%1000000007;

    d=d%1000000007;

    e=e%1000000007;

    f=f%1000000007;

    if(n%6==1)

    {

        while(a<0)

        {

            a=a+1000000007;

        }

        printf("%lld",a);

    }

    else if(n%6==2)

    {

        while(b<0)

        {

            b=b+1000000007;

        }

        printf("%lld",b);

    }

    else if(n%6==3)

    {

        while(c<0)

        {

            c=c+1000000007;

        }

        printf("%lld",c);

    }    

    else if(n%6==4)

    {

        while(d<0)

        {

            d=d+1000000007;

        }

        printf("%lld",d);

    }

    else if(n%6==5)

    {

        while(e<0)

        {

            e=e+1000000007;

        }

        printf("%lld",e);

    }   

    else if(n%6==0)

    {

        while(f<0)

        {

            f=f+1000000007;

        }

        printf("%lld",f);

    }    

	return 0;

}
