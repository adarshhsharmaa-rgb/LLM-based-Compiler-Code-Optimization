// category: repeated_expr  (real program 008)
// Codeforces submission 6400363, problem 417/A, GNU C++, 2014-04-18
// https://codeforces.com/contest/417/submission/6400363
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
using namespace std;
int main()
{
  int c,d,n,m,k;
  scanf("%d%d%d%d%d",&c,&d,&n,&m,&k);
  int sum=n*m-k;
  if(sum<=0) printf("0");
  else if(d*n<c) printf("%d",sum*d);
  else if(sum%n*d<c)
    printf("%d",sum/n*c+sum%n*d);
  else
    printf("%d",sum/n*c+c);
  return 0;
}
