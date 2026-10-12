// category: arithmetic  (real program 008)
// Codeforces submission 20949673, problem 678/A, GNU C11, 2016-09-27
// https://codeforces.com/contest/678/submission/20949673
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>



int main()

{

long long int n,k;

scanf("%lld %lld",&n,&k);



long long int r=n%k;

long long int s=n-r+k;



printf("%lld",s);

return 0;

}
