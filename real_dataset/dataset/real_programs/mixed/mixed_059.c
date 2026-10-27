// category: mixed  (real program 059)
// Codeforces submission 358856, problem 70/A, MS C++, 2011-03-26
// https://codeforces.com/contest/70/submission/358856
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
int a,i;
unsigned long b;

scanf("%d",&a);
if(a<0 || a>1000)return 0;


b=1;

for(i=0;i<a-1;i++){
	b *= 3;
	if(b>1000003)b%=1000003;
}
b%=1000003;
printf("%d\n",b);

return 0;
}
