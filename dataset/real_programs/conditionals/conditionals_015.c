// category: conditionals  (real program 015)
// Codeforces submission 33562535, problem 904/A, GNU C, 2017-12-23
// https://codeforces.com/contest/904/submission/33562535
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>	
int main()
{
	int v1,v2,v3,v4,s1,s2,s3;
	scanf("%d%d%d%d",&v1,&v2,&v3,&v4);
	if (v3*2<v4 || v2 <= v4 || 2*v4 < v3)
		printf("-1\n");
	else
	{
	    if (v4>v3) s3 = v4;
	    else s3= v3;
	    s2=v2*2;
	    s1 = v1*2;
	    printf("%d\n%d\n%d\n",s1,s2,s3);
	}
	return 0;

}
