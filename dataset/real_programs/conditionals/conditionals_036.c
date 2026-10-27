// category: conditionals  (real program 036)
// Codeforces submission 490882, problem 90/A, GNU C++, 2011-06-16
// https://codeforces.com/contest/90/submission/490882
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

using namespace std;

int main()
{
	int r,g,b;
	scanf("%d%d%d",&r,&g,&b);
	int tr=0,tg=0,tb=0;
	int i=0,j=0,k=0;
	i=r/2;
	if(r%2!=0)
		i++;
	j=g/2;
	if(g%2!=0)
		j++;
	k=b/2;
	if(b%2!=0)
		k++;
	if(r!=0)
	tr=30+(i-1)*3;
	if(g!=0)
	tg=31+(j-1)*3;
	if(b!=0)
	tb=32+(k-1)*3;
	int max;
	if(tb>tg)
		max = tb;
	else
		max = tg;
	if(max<tr)
		max = tr;
	printf("%d\n",max);
	return 0;
}
