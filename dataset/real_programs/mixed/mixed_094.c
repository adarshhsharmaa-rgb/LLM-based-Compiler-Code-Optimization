// category: mixed  (real program 094)
// Codeforces submission 19890903, problem 577/A, GNU C, 2016-08-15
// https://codeforces.com/contest/577/submission/19890903
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

	int n,x,i,j,p=0;

	scanf("%d%d",&n,&x);

	for(i=1;i<=n;i++)

	{

  	  if(x%i==0)

  	  {

  	  	if(x/i<=n)

  	  	p++;

		}

	}

	printf("%d",p);

	}
