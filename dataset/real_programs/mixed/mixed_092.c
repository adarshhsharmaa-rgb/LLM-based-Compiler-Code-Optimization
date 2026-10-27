// category: mixed  (real program 092)
// Codeforces submission 6019518, problem 320/A, GNU C++, 2014-03-15
// https://codeforces.com/contest/320/submission/6019518
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
 main()
{
	int k,n,i=0;
	scanf("%d",&n);
	while(n>0)
	{
		if(n%10==1){n=n/10;}
		else if(n%100==14){n=n/100;}
		else if(n%1000==144){n=n/1000;}
		else{i++;n=-1;}
	}
	if(i==0)
		printf("YES");
	if(i>0)
		printf("NO");
	}
