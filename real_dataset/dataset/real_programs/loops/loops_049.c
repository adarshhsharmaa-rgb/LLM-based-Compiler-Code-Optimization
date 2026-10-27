// category: loops  (real program 049)
// Codeforces submission 10852039, problem 491/A, GNU C++, 2015-04-24
// https://codeforces.com/contest/491/submission/10852039
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int a,b,i;

int main(){

	scanf("%d %d",&a,&b);
   
   int st = b+1;

   for(i = 0; i <= a; i++)
		printf("%d ",st+i);
	for(i = 1; i <= b; i++)
		printf("%d ",st-i);

	return 0;
}
