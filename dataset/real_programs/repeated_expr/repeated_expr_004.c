// category: repeated_expr  (real program 004)
// Codeforces submission 21794198, problem 359/B, C++14 (GCC 6-32), 2016-10-26
// https://codeforces.com/contest/359/submission/21794198
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

main(){

	int n,k,i;

	scanf("%d %d",&n,&k);

	for(i=1;i<=k;i++)

	printf("%d %d ",i*2-1,i*2);

	for(i=k+1;i<=n;i++)

	printf("%d %d ",i*2,i*2-1);

}
