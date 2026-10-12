// category: mixed  (real program 073)
// Codeforces submission 17240607, problem 660/B, GNU C++, 2016-04-08
// https://codeforces.com/contest/660/submission/17240607
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
#define ll long long
# define pb push_back
# define mp make_pair
int main()
{
	int n,m,tmp;
	scanf("%d %d",&n,&m);
	int i,x,z;
	x=2*n;
	x++;
	z=x;
	tmp=1;
	while(tmp<z||x<=m)
	{
		if(x<=m)
		printf("%d ",x);
		if(tmp<=m)
		printf("%d ",tmp);
		x++;tmp++;
	}
	printf("\n");
	return 0;
}
