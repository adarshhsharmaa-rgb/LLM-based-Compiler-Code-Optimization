// category: repeated_expr  (real program 007)
// Codeforces submission 13604202, problem 285/A, GNU C++, 2015-10-14
// https://codeforces.com/contest/285/submission/13604202
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include "stdio.h"
main(){
    int n,k;
    scanf("%d %d",&n,&k);
    for(int i=n;i>n-k;i--) printf("%d ",i);
    for(int i=1;i<=n-k;i++) printf("%d ",i);
    return 0;
}
