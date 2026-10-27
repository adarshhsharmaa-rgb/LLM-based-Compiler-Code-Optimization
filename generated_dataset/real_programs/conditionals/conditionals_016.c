// category: conditionals  (real program 016)
// Codeforces submission 21874983, problem 732/C, GNU C++, 2016-10-29
// https://codeforces.com/contest/732/submission/21874983
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>	

main(){

	long long int a,b,c;

	scanf("%lld%lld%lld",&a,&b,&c);

	long long int max=a;

	if(b>max)

	max=b;

	if(c>max)

	max=c;

	max--;

	long long int ans=0;

	if(max>a)

	ans+=max-a;

	if(max>b)

	ans+=max-b;

	if(max>c)

	ans+=max-c;

	printf("%lld",ans);

}
