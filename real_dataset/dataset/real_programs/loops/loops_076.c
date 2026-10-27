// category: loops  (real program 076)
// Codeforces submission 44637768, problem 1031/A, GNU C11, 2018-10-21
// https://codeforces.com/contest/1031/submission/44637768
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(void) {
  int l,b,k,s=0,i,x;
  scanf("%d%d%d",&l,&b,&k);
  for(i=0;i<k;i++)
  {
      x=2*(l+b-2);
      s=s+x;
      l=l-4;
      b=b-4;
  }
  printf("%d",s);
	return 0;
}
