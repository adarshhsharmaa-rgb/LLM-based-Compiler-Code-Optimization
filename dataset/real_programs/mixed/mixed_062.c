// category: mixed  (real program 062)
// Codeforces submission 21980309, problem 732/A, GNU C++11, 2016-11-02
// https://codeforces.com/contest/732/submission/21980309
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

using namespace std;

int k,r,ans;

int main()

{

  scanf("%d%d",&k,&r);

  for(int i=1;i<=15;++i)

  {

  	ans=i*k;ans=ans%10;

  	if(ans==r || ans==0)

  	  {printf("%d",i);return 0;}

  }

}
