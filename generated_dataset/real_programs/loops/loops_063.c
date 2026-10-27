// category: loops  (real program 063)
// Codeforces submission 16256119, problem 630/L, GNU C++, 2016-02-21
// https://codeforces.com/contest/630/submission/16256119
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
#define ll long long
int n,num;
ll ans=1ll;
int main()
{
  scanf("%d",&n);
  num=n/10000*10000+n/100%10*1000+n%10*100+n/10%10*10+n/1000%10;
  for(int i=1;i<=5;i++)
    ans=ans*num%100000;
  printf("%05d\n",ans);
  return 0;
}
