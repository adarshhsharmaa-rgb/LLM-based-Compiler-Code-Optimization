// category: loops  (real program 077)
// Codeforces submission 21501006, problem 268/B, GNU C, 2016-10-16
// https://codeforces.com/contest/268/submission/21501006
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

main()

{

	int n,i,s=0;

	scanf("%d",&n);

	for(i=2;i<=n;i++)

	s=s+(i*(n-i)+1);

	printf("%d",s+n);

}
