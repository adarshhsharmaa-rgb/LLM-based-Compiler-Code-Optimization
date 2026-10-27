// category: mixed  (real program 075)
// Codeforces submission 33289287, problem 898/A, GNU C++, 2017-12-16
// https://codeforces.com/contest/898/submission/33289287
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
#include<cstring>
#include<algorithm>

using namespace std;




int main()
{
	int n;
	scanf("%d",&n);
	int t1=n,t2=n;
	if(n%10==0)printf("%d",n);
	for(int i=1;i<=5;i++)
	{
		t1++;
		if(t1%10==0){
		printf("%d",t1);return 0;
		}
		t2--;
		if(t2%10==0){printf("%d",t2);
		return 0;}
	}
	
	
	return 0;
}
