// category: dead_code  (real program 024)
// Codeforces submission 33568955, problem 904/A, MS C++, 2017-12-23
// https://codeforces.com/contest/904/submission/33568955
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
using namespace std;
int ans=0;
int main()
{
	int v1,v2,v3,v;
	scanf("%d%d%d%d",&v1,&v2,&v3,&v);
	int ans1=2*v1;
	int ans2=2*v2;
	if (v3>=v)
	{
		if (v3<=2*v)
		{
			int ans3=v3;
			if (v*2>=ans2) printf("-1");
			else printf("%d\n%d\n%d\n",ans1,ans2,ans3);
		 } 
		 else printf("-1");
	}
	else 
	{
		if (v<=2*v3)
		{
			int ans3=v;
			if (v*2>=ans2) printf("-1");
			else printf("%d\n%d\n%d\n",ans1,ans2,ans3);
		}
		else printf("-1");
	}
	return 0;
}
