// category: nested  (real program 030)
// Codeforces submission 20312095, problem 622/B, GNU C11, 2016-08-31
// https://codeforces.com/contest/622/submission/20312095
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

	int a,b,c;

	scanf("%d:%d",&a,&b);

	scanf("%d",&c);

	b=b+a*60+c;

	printf("%0.2d:%0.2d\n",(b/60)%24,b%60);

	return 0;

}
